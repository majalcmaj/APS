from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.views import View

from acquisition_presentation_server.common import AlertManager


class AlertsCleaner(LoginRequiredMixin, View):
    login_url = '/aps/login/'

    def post(self, request, *args, **kwargs):
        client_pk = kwargs["client_pk"]
        if request.POST.get('delete_single'):
            AlertManager.delete_alert(int(request.POST.get("alert_pk")))
        if request.POST.get('delete_all'):
            AlertManager.delete_all_for_client(client_pk)
        return HttpResponseRedirect(
            "{}#alerts".format(reverse("aps:ClientDetails", kwargs={"client_pk": client_pk})))
