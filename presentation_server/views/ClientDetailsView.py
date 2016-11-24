import json
import time

from django.http.response import Http404
from django.shortcuts import render
from django.views import View

from common.libs import ClientManager, DataProvider


class ClientDetailsView(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs['client_pk']
        client = ClientManager.get_client(pk)
        if client is None:
            raise Http404
        client_data, _ = DataProvider.get_client_data(client, int(time.time()) - client.monitoring_timespan)
        monitoring_data = json.dumps(client_data) \
            if client.is_configured and client_data is not None else []
        context = {"client": client, "monitoring_data": monitoring_data,
                   "update_ratio_seconds": 5, "alerts": ClientManager.get_client_alerts(client)}
        return render(request, 'presentation_server/ClientDetailView.html', context)
