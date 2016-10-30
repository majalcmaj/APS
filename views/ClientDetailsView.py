import json

from django.shortcuts import render, get_object_or_404
from django.views import View

from acquisition_presentation_server.common.DataProvider import get_client_data
from acquisition_presentation_server.models import Client

class ClientDetailsView(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs['client_pk']
        client = get_object_or_404(Client, pk=pk)
        client_data, _ = get_client_data(client, 120)
        monitoring_data = json.dumps(get_client_data(client, 120)) if client.is_configured else []
        context = {"client" : client, "monitoring_data":monitoring_data}
        return render(request, 'acquisition_presentation_server/ClientDetailView.html', context)