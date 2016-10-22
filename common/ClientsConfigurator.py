import json
from http import client
from pydoc import cli

import requests

from acquisition_presentation_server.models import Client, MonitoredProperties


class ClientsConfigurator:
    def __init__(self, pk, hostname, port, probing_interval, monitored_properties):
        self._pk = pk
        self._hostname = hostname
        self._port = port
        self._probing_interval = probing_interval
        self._monitored_properties = monitored_properties

    def send_configuration(self):
        client = Client.objects.get(pk=self._pk)
        client.hostname = self._hostname
        client.port = self._port
        client.probing_interval = int(self._probing_interval)

        currently_monitored = client.monitored_properties.all()
        currently_monitored_names = set([item.name for item in list(currently_monitored)])
        new_monitored_names = set(self._monitored_properties)
        to_delete = currently_monitored_names - new_monitored_names
        to_add = new_monitored_names - currently_monitored_names

        for name_to_del in to_delete:
            client.monitored_properties.remove(
                MonitoredProperties.objects.get(name=name_to_del))

        print(self._monitored_properties)
        for name_to_add in to_add:
            client.monitored_properties.add(
                MonitoredProperties.objects.get(name=name_to_add))
        self._send_data_to_client(client)  # throws error when cannot connect
        client.save()

    def _send_data_to_client(self, client):
        url = "http://{}:{}".format(client.ip_address, 13000)
        headers = {"content-type": "aps/json"}
        payload = {
            "data_type": "configuration",
            "monitoring_parameters": " ".join(self._monitored_properties), # list(self._monitored_properties),
            "probing_interval": self._probing_interval
        }
        print(payload)
        response = requests.post(url, data=json.dumps(payload), headers=headers)
