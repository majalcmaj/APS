from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse
from django.views import View

from acquisition_presentation_server.common.ClientsStateManager import ClientsStateManager
from acquisition_presentation_server.models import PendingClient, BlockedClient


class BlockedClientsView(LoginRequiredMixin, View):
    login_url = '/aps/login/'
    def get(self, request, *args, **kwargs):
        blocked_clients = BlockedClient.objects.all()
        context = {"current_url": request.get_full_path(), "blocked_clients": blocked_clients}
        return render(request, 'acquisition_presentation_server/BlockedClientsView.html', context)

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('blocked_client_pk')

        if request.POST.get('accept'):
            ClientsStateManager.accept_blocked_client(pk)

        return HttpResponseRedirect(request.get_full_path())
