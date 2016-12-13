import json
import logging

from django.http.response import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from APS.settings import LOGGER_NAME
from common.libs import ClientsConfigurator
from common.libs import ClientsStateManager, ClientManager
from common.libs import MonitoringDataManager
from common.libs.ClientsStateManager import ClientsManagerException

logger = logging.getLogger(LOGGER_NAME)


class JsonRequestView(View):
    # Security block othweriwse
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        #logger.error("{}: {}".format(request.content_type, request.body))
        if request.content_type == "aps/json":
            try:
                json_data = json.loads(request.body.decode('utf-8'))
                message = json_data['message']
                if message == 'monitoring_data':
                    client = ClientManager.get_client(self._extract_client_key(json_data))
                    if client is not None:
                        if client.configuration_pending is True:
                            return self._return_client_configuration(client)
                        else:
                            MonitoringDataManager.process_data(client, json_data['monitored_properties'],
                                                               json_data["timestamp"])
                            return JsonResponse({"result": "success"})
                    else:
                        logger.error("Client with key {} does not exist in database. Address: {}".format(
                            json_data['key'],
                            request.META['REMOTE_ADDR']))
                        return JsonResponse({"result": "failure"})

                elif message == 'is_key_valid':
                    client = ClientManager.get_client_anystate(
                        self._extract_client_key(json_data))
                    return JsonResponse({"key_valid": client is not None})

                elif message == 'get_client_configuration':
                    client = ClientManager.get_client_anystate(
                        self._extract_client_key(json_data))
                    if client is not None:
                        if client.configuration_pending or client.is_configured:
                            return self._return_client_configuration(client)
                    else:
                        logger.error("Client with key {} does not exist in database. Address: {}".format(
                            json_data['key'],
                            request.META['REMOTE_ADDR']))
                    return JsonResponse({"configuration": None})

                elif message == 'register':
                    return self._register_client(json_data, request)
            except ValueError:
                pass
        return JsonResponse(status=400, data={"content": "Bad request"})

    def _return_client_configuration(self, client):
        configuration = ClientsConfigurator.form_configuration_data_for_client(client)
        ClientsConfigurator.ack_configuration_applied(client)
        return JsonResponse({"result": "success", "configuration": configuration})

    def _register_client(self, json_data, request):
        try:
            pk = ClientsStateManager.register_new_pending_client(json_data['hostname'],
                                                                 request.META['REMOTE_ADDR'],
                                                                 json_data['monitored_properties'],
                                                                 json_data['base_probing_interval'],
                                                                 )

            return JsonResponse({"result": "success", "key": pk})
        except ClientsManagerException as e:
            return JsonResponse({"result": "failed", "message": e.message}, status=403)

    def _extract_client_key(self, json_data):
        try:
            return int(json_data.get('key'))
        except TypeError:
            raise ValueError
