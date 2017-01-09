from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls.base import reverse
from django.views import View
from django.views.generic.list import ListView

from common.libs import ClientsStateManager, ClientManager


class PendingClientsView(LoginRequiredMixin, ListView):
    login_url = '/aps/login/'
    template_name = "presentation_server/PendingClientsView.html"

    def get_queryset(self):
        return ClientManager.get_all_pending()

    def post(self, request, *args, **kwargs):
        try:
            pk = request.POST.get('pending_client_pk')

            if request.POST.get('block'):
                ClientsStateManager.block_pending_client(pk)

            if request.POST.get('accept'):
                ClientsStateManager.accept_pending_client(pk)
                return HttpResponseRedirect(
                    reverse("aps:ClientConfiguration", kwargs={"client_pk": pk}))

            return HttpResponseRedirect(request.get_full_path())
        except Exception:
            raise Http404
