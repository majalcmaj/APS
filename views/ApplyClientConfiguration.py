from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.views import View

from acquisition_presentation_server.common.ClientsConfigurator import ClientsConfigurator
from acquisition_presentation_server.common.ClientsStateManager import ClientsStateManager
from acquisition_presentation_server.models import PendingClient, BlockedClient, Client


class ApplyClientConfiguration(View):
    def post(self, request, *args, **kwargs):
        pk = request.POST.get('client_pk')
        ClientsConfigurator.send_configuration(pk)
        return HttpResponseRedirect(reverse('aps:ClientsList'))