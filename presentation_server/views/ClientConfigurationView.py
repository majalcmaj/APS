from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls.base import reverse
from django.views import View

from common.libs import ClientManager, ClientsConfigurator
from presentation_server.views.forms.ClientConfigurationForm import ClientConfigurationForm
from presentation_server.views.forms.ThresholdForm import ThresholdForm


class ClientConfigurationView(LoginRequiredMixin, View):
    login_url = '/aps/login/'

    def get(self, request, *args, **kwargs):
        pk = kwargs['client_pk']
        error = kwargs['error_message']
        error_message = error if error != None else ""
        client = ClientManager.get_client(pk)
        if client is None:
            raise Http404
        return render(request, 'presentation_server/ClientConfigurationView.html',
                      self._create_context(
                          request,
                          client))

    def post(self, request, *args, **kwargs):
        pk = kwargs['client_pk']
        client_conf = ClientConfigurationForm(request.POST)
        monitored_properties = request.POST.getlist('monitored_properties[]')
        property_for_dashboard = request.POST.get('show_on_dashboard[]')
        if client_conf.is_valid():
            redirect_kwargs = {"client_pk": pk}
            try:
                ClientsConfigurator.apply_configuration(
                    pk,
                    client_conf.cleaned_data["hostname"],
                    client_conf.cleaned_data["consecutive_probes_sent_count"],
                    [int(m) for m in monitored_properties],
                    property_for_dashboard,
                    client_conf.get_monitoring_timespan()
                )
            except Exception as e:
                redirect_kwargs["error_message"] = str(e)
                return HttpResponseRedirect(reverse("aps:ClientConfiguration", kwargs=redirect_kwargs))
            return HttpResponseRedirect(reverse("aps:ClientDetails", kwargs=redirect_kwargs))
        else:
            return render(request, 'acquisition_presentation_server/ClientConfigurationView.html',
                          self._create_context(
                              request,
                              ClientManager.get_client(pk),
                              client_conf))

    def _create_context(self, request, client, client_form=None):
        monitored_properies = []
        for property in ClientManager.get_monitored_properties(client):
            monitored_properies.append(
                {
                    "pk": property.pk,
                    "name": property.name,
                    "type": property.type,
                    "checked": property.monitored,
                    "on_dashboard": property.name == client.property_on_dashboard.name if
                    client.property_on_dashboard is not None else False,
                    "thresholds": property.thresholds.all()
                }
            )

        return {
            "client_pk": client.pk,
            "current_url": request.get_full_path(),
            "form": ClientConfigurationForm.from_client(client) if client_form is None else client_form,
            "threshold_form": ThresholdForm.for_client(client.pk),
            "monitored_properties": monitored_properies
        }
