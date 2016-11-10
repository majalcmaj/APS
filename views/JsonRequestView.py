import json
import logging

from django.http.response import JsonResponse, Http404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from acquisition_presentation_server.common.ClientsStateManager import ClientsStateManager, ClientsManagerException
from acquisition_presentation_server.common.ManageMonitoringData import ManageMonitoringData
from acquisition_presentation_server.settings import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)
class JsonRequestView(View):
    # Security block othweriwse
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logger.debug("{}: {}".format(request.content_type, request.body))
        if request.content_type == "aps/json":
            json_data = json.loads(request.body.decode('utf-8'))
            if json_data['message'] == 'register':
                try:
                    ClientsStateManager.register_new_pending_client(json_data['hostname'],
                                                                    request.META['REMOTE_ADDR'],
                                                                    json_data['listening_port'],
                                                                    json_data['monitored_properties'])


                except ClientsManagerException as e:
                    return JsonResponse({"result": "failed", "message": e.message}, status=403)
                return JsonResponse({"result": "success"})
            elif json_data['message'] == 'monitoring_data':
                ManageMonitoringData.process_data(request.META['REMOTE_ADDR'], json_data['monitored_properties'])
                return JsonResponse({"result": "success"})
