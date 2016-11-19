import json

import time
from django.shortcuts import render, get_object_or_404
from django.views import View

from acquisition_presentation_server.common.DataProvider import get_client_data
from acquisition_presentation_server.models import Client


class ClientDetailsView(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs['client_pk']
        client = get_object_or_404(Client, pk=pk)
        client_data, _ = get_client_data(client, int(time.time()) - 120)
        monitoring_data = json.dumps(client_data) \
            if client.is_configured and client_data is not None else []
        context = {"client": client, "monitoring_data": monitoring_data,
                   "update_ratio_seconds": 5, "alerts":client.alerts.all()}
        return render(request, 'acquisition_presentation_server/ClientDetailView.html', context)
