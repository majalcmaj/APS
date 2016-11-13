import json
import logging
from http import client
from pydoc import cli

import requests
from django.db import transaction
from django.http.response import HttpResponseServerError

from acquisition_presentation_server.common.RRDtoolManager import RRDtoolManager
from acquisition_presentation_server.models import Client, MonitoredProperty
from acquisition_presentation_server.settings import LOGGER_NAME
from ..models import ClientBase, Threshold, MonitoredProperty

logger = logging.getLogger(LOGGER_NAME)


class ClientsConfigurator:
    def __init__(self, pk, hostname, probing_cycles, monitored_properties,
                 property_for_dashbaord):
        self._pk = pk
        self._hostname = hostname
        self._probing_cycles = probing_cycles
        self._monitored_properties = monitored_properties
        self._prop_on_dashboard = property_for_dashbaord

    @transaction.atomic
    def apply_configuration(self):
        client = Client.objects.get(pk=self._pk)
        client.configuration_pending = True
        client.hostname = self._hostname
        client.probing_interval = int(self._probing_cycles)

        if self._prop_on_dashboard is not None:
            client.property_on_dashboard = client.monitored_properties.get(
                pk=self._prop_on_dashboard
            )

        for m in client.monitored_properties.all():
            # m.thresholds.all().delete()
            m.monitored = True if m.pk in self._monitored_properties else False
            m.save()

        # for t in self._thresholds:
        #     threshold = Threshold(type = 1,
        #                           value = t[1],
        #                           max_cycle_above_value=t[2],
        #                           monitored_property=MonitoredProperty.objects.get(pk=t[0]+1))
        #     threshold.save()
        #
        # for m in MonitoredProperty.objects.all():
        #     print(m.pk,end=' ')
        #     for t in m.thresholds.all():
        #         print(t.type,t.value)


        client.is_configured = True
        client.save()
        RRDtoolManager(client).create_rrd()

    @staticmethod
    def form_configuration_data_for_client(client):
        if client.is_configured:
            configuration = {
                "monitoring_parameters": [mp.name for mp in
                                          client.monitored_properties.filter(monitored=True)],
                "probing_interval": client.probing_interval
            }
            return configuration
        else:
            return None

    @staticmethod
    @transaction.atomic
    def change_client_configuration_status(pk, status):
        clients = ClientBase.objects.filter(pk=pk)
        if len(clients) == 1:
            clients[0].configuration_pending = status
            clients[0].save()


class ClientConfigurationException(BaseException):
    def __init__(self, message=None):
        self._message = "Error during configuring client" if message is None else message
        super().__init__(self._message)

    @property
    def message(self):
        return self._message
