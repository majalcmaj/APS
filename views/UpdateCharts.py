import json

import time

from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from acquisition_presentation_server.common.DataProvider import get_client_data
from acquisition_presentation_server.models import PendingClient, BlockedClient, Client, MonitoredProperty

class UpdateCharts(View):
    # TODO: Dodać csrf do ajaxa w index.html
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        client_pks = json.loads(request.POST.get('client_pks'))
        last_timestamp = request.POST.get("most_recent_timestamp")
        current_time = int(time.time())
        client_data, new_timestamp = get_client_data(Client.objects.get(), current_time - int(last_timestamp))
        response = {
            "monitoring_data":{client_pk:client_data for client_pk in client_pks},
            "timestamp":new_timestamp
        }
        return JsonResponse(response)
