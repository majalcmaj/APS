from django.http.response import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import render
from django.urls.base import reverse
from django.views.generic.base import View

from common.libs import ClientManager, ClientsConfigurator
from presentation_server.views.forms.MultipleClientConfigurationForm import MultipleClientConfigurationForm


class MultipleConfigureView(View):
    def post(self, request, *args, **kwargs):
        if request.POST.get("begin_configuration") is not None:
            pks = [int(pk) for pk in self.request.POST.getlist("pks_to_configure[]")]
            if len(pks) > 0:
                clients = list(ClientManager.get_clients_list(pks))
                context = {
                    "clients_to_configure": clients,
                    "form": MultipleClientConfigurationForm.from_client(clients[0]),
                    "monitored_properties": clients[0].monitored_properties.all()
                }
                return render(request, "presentation_server/MultipleConfigureView.html", context=context)
            else:
                return HttpResponseForbidden()
        elif request.POST.get("apply_configuration") is not None:
            configuration_form = MultipleClientConfigurationForm(request.POST)
            # TODO:Message jak zly.
            if configuration_form.is_valid():
                pks = [int(pk) for pk in request.POST.getlist("pks_to_configure[]")]
                property_for_dashboard = request.POST.get('show_on_dashboard[]')
                monitored_properties = request.POST.getlist('monitored_properties[]')
                ClientsConfigurator.configure_multiple(
                    pks,
                    configuration_form.cleaned_data["consecutive_probes_sent_count"],
                    configuration_form.get_monitoring_timespan(),
                    monitored_properties,
                    property_for_dashboard
                )
            return HttpResponseRedirect(reverse("aps:MultipleConfigureList"))
        else:
            raise Http404
