import json

from django.shortcuts import render
from django.views import View

from acquisition_presentation_server.common.DataProvider import get_client_data
from acquisition_presentation_server.models import Client

class IndexView(View):
    def get(self, request, *args, **kwargs):
        clients_data = []
        for client in Client.objects.all() :
            clients_data.append(
                {
                    "client" : client,
                    "monitoring_data" : json.dumps(get_client_data())
                }
            )
        context = {"clients_data":clients_data}
        return render(request, 'acquisition_presentation_server/index.html', context)