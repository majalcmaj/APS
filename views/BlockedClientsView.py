from django.shortcuts import render
from django.views import View

from acquisition_presentation_server.models import PendingClient, BlockedClient


class BlockedClientsView(View):
    def get(self, request, *args, **kwargs):
        blocked_clients = BlockedClient.objects.all()
        context = {"blocked_clients":blocked_clients}
        return render(request, 'acquisition_presentation_server/BlockedClientsView.html', context)