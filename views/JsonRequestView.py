import json

from django.http.response import JsonResponse, Http404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from acquisition_presentation_server.common.ClientsStateManager import ClientsStateManager, ClientsManagerException


class JsonRequestView(View):

    # Security block othweriwse
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print(request.content_type)
        print(request.body)
        if request.content_type == "aps/json":
            json_data = json.loads(request.body.decode('utf-8'))
            if json_data['message'] == 'register':
                try:
                    ClientsStateManager.register_new_pending_client(request.META['REMOTE_HOST'], request.META['REMOTE_ADDR'])
                except ClientsManagerException as e:
                    return JsonResponse({"result":"failed", "message":e.message}, status=403)
                return JsonResponse({"result": "success"})
