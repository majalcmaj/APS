from django.shortcuts import render, get_object_or_404
from django.views import View

from acquisition_presentation_server.models import PendingClient, BlockedClient, Client, MonitoredProperties

class ClientConfigurationView(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs['client_pk']
        error_message = kwargs['error_message']
        client = get_object_or_404(Client, pk=pk)
        monitored_properies = []
        for property in MonitoredProperties.objects.all():
            monitored_properies.append(
                (property.name, property.type, "checked" if
                len(client.monitored_properties.filter(name=property.name))>0 else ""))
        context = {"client" : client, 'monitored_properties' : monitored_properies, "error_message":error_message}
        return render(request, 'acquisition_presentation_server/ClientConfigurationView.html', context)