from django.shortcuts import render
from django.views import View

from acquisition_presentation_server.models import PendingClient


class PendingClientsView(View):
    def get(self, request, *args, **kwargs):
        pending_clients = PendingClient.objects.all()
        context = {"pending_clients":pending_clients}
        return render(request, 'acquisition_presentation_server/PendingClientsView.html', context)