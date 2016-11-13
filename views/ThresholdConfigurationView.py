import logging
import re
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls.base import reverse
from django.views import View

from acquisition_presentation_server.common import ThresholdConfigurator
from acquisition_presentation_server.common.ClientsConfigurator import ClientsConfigurator
from acquisition_presentation_server.models import PendingClient, BlockedClient, Client, MonitoredProperty
from acquisition_presentation_server.views.forms.ClientConfigurationForm import ClientConfigurationForm


class ThresholdConfigurationView(LoginRequiredMixin, View):
    login_url = '/aps/login/'

    def post(self, request, *args, **kwargs):
        client_pk = request.POST.get('client_pk')
        if request.POST.get('add_threshold'):
            value = request.POST.get('threshold_value')
            cycles = request.POST.get('threshold_cycles')
            threshold_type = request.POST.get('threshold_type')
            mp_pk = request.POST.get('mp_pk')
            ThresholdConfigurator.add_threshold(value, cycles, threshold_type, mp_pk)
        if request.POST.get('delete_threshold'):
            threshold_pk = request.POST.get("threshold_pk")
            ThresholdConfigurator.delete_threshold(threshold_pk)
        return HttpResponseRedirect(
            reverse("aps:ClientConfiguration", kwargs={"client_pk": client_pk}))
