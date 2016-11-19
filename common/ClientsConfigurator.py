import logging

from django.db import transaction

from acquisition_presentation_server.common import RRDtoolManager
from acquisition_presentation_server.models import Client
from acquisition_presentation_server.settings import LOGGER_NAME

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

        client.is_configured = True
        client.save()
        RRDtoolManager.create_rrd(client)

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
    def change_client_configuration_status(client, status):
        client.configuration_pending = status
        client.save()


class ClientConfigurationException(BaseException):
    def __init__(self, message=None):
        self._message = "Error during configuring client" if message is None else message
        super().__init__(self._message)

    @property
    def message(self):
        return self._message
