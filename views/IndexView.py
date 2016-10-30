import json

from django.shortcuts import render
from django.views import View
import time

from acquisition_presentation_server.common.DataProvider import get_client_data
from acquisition_presentation_server.models import Client

class IndexView(View):
    def get(self, request, *args, **kwargs):
        clients = list(Client.objects.all())
        monitoring_data = {client.pk:(get_client_data(client, 120)[0] if client.is_configured else []) for client in clients}
        context = {"clients":clients, "monitoring_data":json.dumps(monitoring_data), "timestamp":int(time.time()), "update_ratio_seconds":5}
        return render(request, 'acquisition_presentation_server/index.html', context)