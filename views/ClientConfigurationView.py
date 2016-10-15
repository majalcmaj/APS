from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls.base import reverse
from django.views import View

from acquisition_presentation_server.common.ClientsStateManager import ClientsStateManager
from acquisition_presentation_server.models import PendingClient, BlockedClient, Client, MonitoredProperties


class ClientConfigurationView(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs['client_pk']
        print(pk)
        client = get_object_or_404(Client, pk=pk)
        print(client)
        monitored_properties_set = client.monitoredproperties_set.all()
        monitored_properies = {}
        for choice in MonitoredProperties.get_possible_choices():
            monitored_properies[choice] = True if choice in monitored_properties_set else False
        context = {"client" : client, 'possible_monitored_properties' : monitored_properies}
        return render(request, 'acquisition_presentation_server/ClientConfigurationView.html', context)