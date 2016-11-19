from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.views import View

from acquisition_presentation_server.common import ThresholdConfigurator
from acquisition_presentation_server.views.forms.ThresholdForm import ThresholdForm


class ThresholdConfigurationView(LoginRequiredMixin, View):
    login_url = '/aps/login/'

    def post(self, request, *args, **kwargs):
        client_pk = request.POST.get('client_pk')
        if request.POST.get('add_threshold'):
            form = ThresholdForm(request.POST)
            if form.is_valid():
                mp_pk = request.POST.get('mp_pk')
                value = form.cleaned_data['value']
                cycles = form.cleaned_data['cycles_above']
                threshold_type = form.cleaned_data['type']
                ThresholdConfigurator.add_threshold(value, cycles, threshold_type, mp_pk)

        if request.POST.get('delete_threshold'):
            threshold_pk = request.POST.get("threshold_pk")
            ThresholdConfigurator.delete_threshold(threshold_pk)
        return HttpResponseRedirect(
            "{}#threshold_configuration".format(reverse("aps:ClientConfiguration", kwargs={"client_pk": client_pk})))
