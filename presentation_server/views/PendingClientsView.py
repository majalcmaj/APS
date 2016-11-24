from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views import View

from common.libs import ClientsStateManager, ClientManager


class PendingClientsView(LoginRequiredMixin, View):
    login_url = '/aps/login/'

    def get(self, request, *args, **kwargs):
        pending_clients = ClientManager.get_all_pending()
        context = {"current_url": request.get_full_path(), "pending_clients": pending_clients}
        return render(request, 'presentation_server/PendingClientsView.html', context)

    def post(self, request, *args, **kwargs):
        try:
            pk = request.POST.get('pending_client_pk')

            if request.POST.get('block'):
                ClientsStateManager.block_pending_client(pk)

            if request.POST.get('accept'):
                ClientsStateManager.accept_pending_client(pk)
                return HttpResponseRedirect("/aps/ClientConfiguration/{}".format(pk))

            return HttpResponseRedirect(request.get_full_path())
        except Exception:
            raise Http404
