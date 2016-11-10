from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse
from django.views import View

from acquisition_presentation_server.common.ClientsStateManager import ClientsStateManager
from acquisition_presentation_server.models import PendingClient


class PendingClientsView(View):
    def get(self, request, *args, **kwargs):
        pending_clients = PendingClient.objects.all()
        context = {"current_url":request.get_full_path(), "pending_clients":pending_clients}
        return render(request, 'acquisition_presentation_server/PendingClientsView.html', context)

    def post(self, request, *args, **kwargs):
        pk = request.POST['pending_client_pk']

        if request.POST.get('block'):
            ClientsStateManager.block_pending_client(pk)

        if request.POST.get('accept'):
            ClientsStateManager.accept_pending_client(pk)

        return HttpResponseRedirect(request.get_full_path())