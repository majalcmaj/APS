from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.views import View

from common.libs import ThresholdManager
from presentation_server.views.forms.ThresholdForm import ThresholdForm


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
                is_gt = form.cleaned_data['gt_or_lt'] == 'gt'
                message_template = form.cleaned_data['message_template']
                ThresholdManager.add_threshold(value, cycles, threshold_type, mp_pk, is_gt, message_template)

        if request.POST.get('delete_threshold'):
            threshold_pk = request.POST.get("threshold_pk")
            ThresholdManager.delete_threshold(threshold_pk)
        return HttpResponseRedirect(
            "{}#threshold_configuration".format(reverse("aps:ClientConfiguration", kwargs={"client_pk": client_pk})))
