from django.shortcuts import render
from django.views import View

from acquisition_presentation_server.models import Client

class IndexView(View):
    def get(self, request, *args, **kwargs):
        clients = Client.objects.all()
        context = {"clients":clients}
        return render(request, 'acquisition_presentation_server/index.html', context)