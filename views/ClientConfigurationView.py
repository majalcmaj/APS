import logging

from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls.base import reverse
from django.views import View

from acquisition_presentation_server.common.ClientsConfigurator import ClientsConfigurator
from acquisition_presentation_server.models import PendingClient, BlockedClient, Client, MonitoredProperty
from acquisition_presentation_server.views.forms.ClientConfigurationForm import ClientConfigurationForm


class ClientConfigurationView(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs['client_pk']
        error = kwargs['error_message']
        error_message = error if error != None else ""
        client = get_object_or_404(Client, pk=pk)

        # "client": client,'monitored_properties': monitored_properies,"error_message": error_message
        return render(request, 'acquisition_presentation_server/ClientConfigurationView.html',
                      self._create_context(
                          request,
                          client))

    def post(self, request, *args, **kwargs):
        pk = kwargs['client_pk']
        client_conf = ClientConfigurationForm(request.POST)
        # hostname = request.POST.get('hostname')
        # port = request.POST.get('port')
        # probing_interval = request.POST.get('probing_interval')
        monitored_properties = request.POST.getlist('monitored_properties[]')
        if client_conf.is_valid():
            cc = ClientsConfigurator(
                pk,
                client_conf.cleaned_data["hostname"],
                client_conf.cleaned_data["port"],
                client_conf.cleaned_data["probing_interval"],
                [int(m) for m in monitored_properties]
            )
            redirect_kwargs = {"client_pk": pk}
            try:
                cc.send_configuration()
            except Exception as e:
                redirect_kwargs["error_message"] = str(e)
            return HttpResponseRedirect(request.get_full_path())
        else:
            return render(request, 'acquisition_presentation_server/ClientConfigurationView.html',
                          self._create_context(
                              request,
                              Client.objects.get(pk=pk),
                              client_conf))

    def _create_context(self, request, client, client_form=None):
        monitored_properies = []
        for property in client.monitored_properties.all():
            monitored_properies.append(
                (property.pk, property.name, property.type, "checked" if
                property.monitored else ""))

        return {
            "current_url": request.get_full_path(),
            "form": ClientConfigurationForm.from_client(client) if client_form is None else client_form,
            "monitored_properties": monitored_properies
        }
