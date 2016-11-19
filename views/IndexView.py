import json

import time
from django.shortcuts import render
from django.views import View

from acquisition_presentation_server.common.DataProvider import get_client_data
from acquisition_presentation_server.models import Client


class IndexView(View):
    def get(self, request, *args, **kwargs):
        clients = list(Client.objects.all())
        monitoring_data = {}
        for client in clients:
            client_data, _ = get_client_data(client, int(time.time()) - 120)
            monitoring_data[client.pk] = client_data \
                if client.is_configured and client_data is not None else []
        context = {"clients": clients, "monitoring_data": json.dumps(monitoring_data), "update_ratio_seconds": 5}
        return render(request, 'acquisition_presentation_server/index.html', context)
