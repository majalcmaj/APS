import json
import re

import time
from django.shortcuts import render
from django.views import View

from common.libs import MonitoringDataManager
from common.libs import ClientManager
from presentation_server.views.forms.FilteringForm import FilteringForm


class IndexView(View):
    def get(self, request, *args, **kwargs):
        clients = ClientManager.get_all_clients()
        return self._render_page(request, clients=clients)

    def post(self, request, *args, **kwargs):
        filtering_form = FilteringForm(request.POST)
        if filtering_form.is_valid():
            regex = filtering_form.cleaned_data["filter_regex"]
            sorting = filtering_form.cleaned_data["sorting"]
            sort_ascending = True if sorting == "h_asc" else False
            return self._render_page(request, ClientManager.get_clients(regex, sort_ascending),
                                     filtering_form)
        else:
            return self._render_page(request, ClientManager.get_all_clients(), filtering_form)

    @staticmethod
    def _render_page(request, clients, filtering_form=None):
        monitoring_data = {}
        for client in clients:
            client_data, _ = MonitoringDataManager.get_client_data(client,
                                                                   int(time.time()) - client.monitoring_timespan)
            monitoring_data[client.pk] = client_data \
                if client.is_configured and client_data is not None else []
        if filtering_form is None:
            filtering_form = FilteringForm()
        context = {
            "clients": clients,
            "monitoring_data": json.dumps(monitoring_data),
            "update_ratio_seconds": 5,
            "filtering_form": filtering_form
        }
        return render(request, 'presentation_server/index.html', context)
