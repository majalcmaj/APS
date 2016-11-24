from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from acquisition_presentation_server.common import ClientManager
from acquisition_presentation_server.common import ClientsStateManager


class BlockedClientsView(LoginRequiredMixin, View):
    login_url = '/aps/login/'
    def get(self, request, *args, **kwargs):
        blocked_clients = ClientManager.get_all_blocked()
        context = {"current_url": request.get_full_path(), "blocked_clients": blocked_clients}
        return render(request, 'acquisition_presentation_server/BlockedClientsView.html', context)

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('blocked_client_pk')

        if request.POST.get('accept'):
            ClientsStateManager.accept_blocked_client(pk)

        return HttpResponseRedirect(request.get_full_path())
