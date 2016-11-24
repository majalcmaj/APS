import logging

from acquisition_presentation_server import settings
from acquisition_presentation_server.common import RRDtoolManager
from acquisition_presentation_server.models import Client

logger = logging.getLogger(settings.LOGGER_NAME)

"""
File contains functions and exceptions used when configuring client
"""

def apply_configuration(pk, hostname, probing_cycles, monitored_properties,
                        property_for_dashboard, monitoring_timespan):
    """
    Applies configuration for the client - sets appropriate values in database, which
    are collected by client at nearest request
    :param pk: Client's public key in database
    :param hostname: Client's hostname
    :param probing_cycles: Count of consecutive probes which are averaged before sending data
    to server
    :param monitored_properties: list of monitoring properties' public key which are desired to be
    monitored
    :param property_for_dashboard: property the chart of which should be present on dashboard
    :param monitoring_timespan: A timespan for which the client should be monitored, in seconds
    :return: None
    :raises: Exception related to client not found and other unwanted operations
    """
    client = Client.objects.get(pk=pk)
    client.configuration_pending = True
    client.hostname = hostname
    client.consecutive_probes_sent_count = int(probing_cycles)
    if client.consecutive_probes_sent_count * client.base_probing_interval > monitoring_timespan:
        raise ClientConfigurationException(message="Timespan has to be greater than "
                                           "probing interval!")
    client.monitoring_timespan = monitoring_timespan

    if property_for_dashboard is not None:
        client.property_on_dashboard = client.monitored_properties.get(
            pk=property_for_dashboard
        )

    for m in client.monitored_properties.all():
        m.monitored = True if m.pk in monitored_properties else False
        m.save()

    client.is_configured = True
    client.save()
    RRDtoolManager.create_rrd(client)


def form_configuration_data_for_client(client):
    """
    Prepare JSON message containing data with client configuration
    :param client: client for which the configuration data should be prepared
    :return: message or none if client is not configured
    """
    if client.is_configured:
        configuration = {
            "monitoring_parameters": [mp.name for mp in
                                      client.monitored_properties.filter(monitored=True)],
            #todo ZMIENIC na consecutive_probes_sent_count!
            "probing_interval": client.consecutive_probes_sent_count
        }
        return configuration
    else:
        return None


def ack_configuration_applied(client):
    """
    Sets switch configuration_pending in client database entry to false, which means
        that there is no new configuration awaiting for client
    :param client: client to alter
    """
    client.configuration_pending = False
    client.save()


class ClientConfigurationException(BaseException):
    """
    Thrown when there is a problem with client configuration
    """
    def __init__(self, message=None):
        self._message = "Error during configuring client" if message is None else message
        super().__init__(self._message)

    @property
    def message(self):
        return self._message
