from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.views import View

from acquisition_presentation_server.common.ClientsStateManager import ClientsStateManager
from acquisition_presentation_server.models import PendingClient, BlockedClient, Client


class PendingClientModify(View):
    def post(self, request, *args, **kwargs):
        pk = request.POST['pending_client_pk']

        if request.POST.get('block'):
            ClientsStateManager.block_pending_client(pk)

        if request.POST.get('accept'):
            ClientsStateManager.accept_pending_client(pk)

        return HttpResponseRedirect(reverse('aps:PendingClients'))