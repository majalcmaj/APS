import json

import time

from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from acquisition_presentation_server.common.DataProvider import get_client_data
from acquisition_presentation_server.common.RRDtoolManager import RRDtoolManager
from acquisition_presentation_server.models import PendingClient, BlockedClient, Client, MonitoredProperty


class UpdateCharts(View):
    # TODO: Dodać csrf do ajaxa w index.html
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pk_last_update = json.loads(request.POST.get("pk_last_update"))
        current_time = int(time.time())
        monitoring_data = {}
        if pk_last_update is not None:
            for pk, timestamp in pk_last_update.items():
                monitoring_data[pk], pk_last_update[pk] = RRDtoolManager(
                    Client.objects.get(pk=pk)).fetch_data(current_time - int(timestamp))
        response = {
            "monitoring_data": monitoring_data,
            "pk_last_update": pk_last_update
        }
        return JsonResponse(response)
