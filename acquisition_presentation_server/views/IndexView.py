import json
import re

import time
from django.shortcuts import render
from django.views import View

from acquisition_presentation_server.common.ClientManager import get_clients, get_all_clients
from acquisition_presentation_server.common.DataProvider import get_client_data
from acquisition_presentation_server.models import Client
from acquisition_presentation_server.views.forms.FilteringForm import FilteringForm


class IndexView(View):
    def get(self, request, *args, **kwargs):
        clients = get_all_clients()
        return self._render_page(request, clients=clients)

    def post(self, request, *args, **kwargs):
        filtering_form = FilteringForm(request.POST)
        if filtering_form.is_valid():
            regex = filtering_form.cleaned_data["filter_regex"]
            sorting = filtering_form.cleaned_data["sorting"]
            sort_ascending = True if sorting == "h_asc" else False
            return self._render_page(request, get_clients(regex, sort_ascending),
                                     filtering_form)
        else:
            return self._render_page(request, get_all_clients(), filtering_form)

    @staticmethod
    def _render_page(request, clients, filtering_form=None):
        monitoring_data = {}
        for client in clients:
            client_data, _ = get_client_data(client, int(time.time()) - client.monitoring_timespan)
            monitoring_data[client.pk] = client_data \
                if client.is_configured and client_data is not None else []
        if filtering_form is None:
            filtering_form=FilteringForm()
        context = {
            "clients": clients,
            "monitoring_data": json.dumps(monitoring_data),
            "update_ratio_seconds": 5,
            "filtering_form":filtering_form
        }
        return render(request, 'acquisition_presentation_server/index.html', context)
