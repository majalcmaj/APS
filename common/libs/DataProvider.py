from common.libs import RRDtoolManager

"""
File contains functions which collect client data for presentation
"""


def get_client_data(client, since):
    """
    Get monitoring data of client since provided time
    :param client: client for which the data should be collected
    :param since: unix timestamp(in seconds); time point since when the data from RRD database should be collected
    :return: monitoring data
    """
    return RRDtoolManager.fetch_data(client, since)


def get_client_alerts(client):
    """
    :param client: Client for which the alerts should be collected
    :return: list of strings representing alerts for given client
    """
    return [alert.created + ": " + alert.message for alert in client.alerts.all()]
