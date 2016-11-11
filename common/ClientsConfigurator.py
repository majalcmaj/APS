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

logger = logging.getLogger(LOGGER_NAME)


class ClientsConfigurator:
    def __init__(self, pk, hostname, probing_interval, monitored_properties, property_for_dashbaord):
        self._pk = pk
        self._hostname = hostname
        self._probing_interval = probing_interval
        self._monitored_properties = monitored_properties
        self._prop_on_dashboard = property_for_dashbaord

    @transaction.atomic
    def send_configuration(self):
        client = Client.objects.get(pk=self._pk)
        client.hostname = self._hostname
        client.probing_interval = int(self._probing_interval)
        if self._prop_on_dashboard is not None:
            client.property_on_dashboard = client.monitored_properties.get(
                pk=self._prop_on_dashboard
            )

        for m in client.monitored_properties.all():
            m.monitored = True if m.pk in self._monitored_properties else False
            m.save()

        response = self._send_data_to_client(client)  # throws error when cannot connect
        if response.status_code != 200:
            msg = "Error code {} returned with message: {}".format(response.status_code, response.json())
            logger.error(msg)
            raise ClientConfigurationException(msg)
        client.is_configured = True
        client.save()
        RRDtoolManager(client).create_rrd()

    def _send_data_to_client(self, client):
        url = "http://{}:{}".format(client.ip_address, client.port)
        headers = {"content-type": "aps/json"}
        payload = {
            "data_type": "configuration",
            "monitoring_parameters": [mp.name for mp in
                                      client.monitored_properties.filter(monitored=True)],
            "probing_interval": self._probing_interval
        }
        return requests.post(url, data=json.dumps(payload), headers=headers)


class ClientConfigurationException(BaseException):
    def __init__(self, message=None):
        self._message = "Error during configuring client" if message is None else message
        super().__init__(self._message)

    @property
    def message(self):
        return self._message
