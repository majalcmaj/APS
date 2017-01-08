from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse
from django.views import View
from django.views.generic.list import ListView

from common.libs import ClientManager, ClientsStateManager


class BlockedClientsView(LoginRequiredMixin, ListView):
    login_url = '/aps/login/'
    template_name = "presentation_server/BlockedClientsView.html"
    # def get(self, request, *args, **kwargs):
    #     blocked_clients = ClientManager.get_all_blocked()
    #     context = {"current_url": request.get_full_path(), "blocked_clients": blocked_clients}
    #     return render(request, 'presentation_server/BlockedClientsView.html', context)

    def get_queryset(self):
        return ClientManager.get_all_blocked()

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('client_pk')

        if request.POST.get('accept'):
            ClientsStateManager.accept_blocked_client(int(pk))
            return HttpResponseRedirect(
                reverse("aps:ClientConfiguration", kwargs={"client_pk": pk}))

        return HttpResponseRedirect(request.get_full_path())
