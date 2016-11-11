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
from ..models import ClientBase

logger = logging.getLogger(LOGGER_NAME)


class ClientsConfigurator:
    def __init__(self, pk, hostname, probing_interval, monitored_properties):
        self._pk = pk
        self._hostname = hostname
        self._probing_interval = probing_interval
        self._monitored_properties = monitored_properties

    @transaction.atomic
    def apply_configuration(self):
        client = Client.objects.get(pk=self._pk)
        client.configuration_pending=True
        client.hostname = self._hostname
        client.probing_interval = int(self._probing_interval)

        for m in client.monitored_properties.all():
            m.monitored = True if m.pk in self._monitored_properties else False
            m.save()
        # currently_monitored_pks = set([item.pk for item in list(currently_monitored)])
        # new_monitored_props = set(self._monitored_properties)
        # stop_monitoring = currently_monitored_pks - new_monitored_props
        # start_monitoring = new_monitored_props - currently_monitored_pks
        # for stop_pk in stop_monitoring:

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
    def change_client_configuration_status(pk,status):
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
