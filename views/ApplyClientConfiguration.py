from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.views import View

from acquisition_presentation_server.common import ClientsConfigurator
from acquisition_presentation_server.common.ClientsConfigurator import ClientsConfigurator
from acquisition_presentation_server.common.ClientsStateManager import ClientsStateManager
from acquisition_presentation_server.models import PendingClient, BlockedClient, Client


class ApplyClientConfiguration(View):
    def post(self, request, *args, **kwargs):
        pk = request.POST.get('client_pk')
        hostname = request.POST.get('hostname')
        probing_interval = request.POST.get('probing_interval')
        monitored_properties = request.POST.getlist('monitored_properties[]')
        print(monitored_properties)
        cc= ClientsConfigurator(pk, hostname, probing_interval, monitored_properties)
        error_message=""
        try:
            cc.send_configuration()
        except Exception as e:
            error_message = str(e)
        return HttpResponseRedirect(reverse(
            'aps:ClientConfiguration',
            kwargs={"client_pk":pk, "error_message":error_message}))