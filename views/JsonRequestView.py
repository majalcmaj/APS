import json
import logging

from django.http.response import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from acquisition_presentation_server.common import ClientsStateManager
from acquisition_presentation_server.common import ManageMonitoringData
from acquisition_presentation_server.common.ClientsConfigurator import ClientsConfigurator
from acquisition_presentation_server.common.ClientsStateManager import ClientsManagerException
from acquisition_presentation_server.models import ClientBase
from acquisition_presentation_server.settings import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class JsonRequestView(View):
    # Security block othweriwse
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logger.error("{}: {}".format(request.content_type, request.body))
        if request.content_type == "aps/json":
            json_data = json.loads(request.body.decode('utf-8'))
            if json_data['message'] == 'register':
                try:
                    pk = ClientsStateManager.register_new_pending_client(json_data['hostname'],
                                                                         request.META['REMOTE_ADDR'],
                                                                         json_data['listening_port'],
                                                                         json_data['monitored_properties'],
                                                                         json_data['base_probing_interval'],
                                                                         )

                    return JsonResponse({"result": "success", "key": pk})
                except ClientsManagerException as e:
                    return JsonResponse({"result": "failed", "message": e.message}, status=403)

            elif json_data['message'] == 'monitoring_data':
                client = ClientsStateManager.get_client(int(json_data['key']))
                if client is not None:
                    if client.configuration_pending is True:
                        configuration = ClientsConfigurator.form_configuration_data_for_client(client)
                        ClientsConfigurator.change_client_configuration_status(client, False)
                        return JsonResponse({"result": "success", "configuration": configuration})
                    else:
                        ManageMonitoringData.process_data(client, json_data['monitored_properties'],
                                                          json_data["timestamp"])
                        return JsonResponse({"result": "success"})
                else:
                    logger.error("Client with key {} does not exist in database. Address: {}".format(
                        json_data['key'],
                        request.META['REMOTE_ADDR']))
                    return JsonResponse({"result": "failure"})

            elif json_data['message'] == 'get_client_configuration':
                client = ClientsStateManager.get_client(int(json_data['key']))
                if client is not None:
                    if client.configuration_pending:
                        configuration = ClientsConfigurator.form_configuration_data_for_client(client)
                        ClientsConfigurator.change_client_configuration_status(client, False)
                        return JsonResponse({"configuration": configuration})
                else:
                    logger.error("Client with key {} does not exist in database. Address: {}".format(
                        json_data['key'],
                        request.META['REMOTE_ADDR']))
                return JsonResponse({"configuration": None})