import re

from common.models import ClientBase, Client, PendingClient, BlockedClient

"""
File contains functions which are used to get clients information from database.
Used for preventing direct operations on database by acquisition and presentation layers
"""


def get_all_clients():
    """
    :return: Queryset of all monitored clients existing in database
    """
    return Client.objects.all()


def get_all_pending():
    """
    :return: Queryset of all pending clients existing in database
    """
    return PendingClient.objects.all()


def get_all_blocked():
    """
    :return: Queryset of all blocked clients existing in database
    """
    return BlockedClient.objects.all()


def get_client(pk):
    """
    :return: Client identified by given public key or None if no such client exists
    """
    try:
        return Client.objects.get(pk=pk)
    except Client.DoesNotExist:
        return None


def get_client_alerts(client):
    """
    :param client: An object representing monitored client, of which alerts should be returned
    :return: All alerts for specified client
    """
    return client.alerts.all()


def get_client_anystate(pk):
    """
    :param pk: Public key identifying client
    :return: object representing client in any state: monitored, pending, blocked, or None
    if no client for given pk exists in database
    """
    try:
        return ClientBase.objects.get(pk=pk)
    except ClientBase.DoesNotExist:
        return None


def get_clients(filter_regex="", sort_ascending=True):
    """
    :param filter_regex: simple regex, where character "*" means any count of any characters;
    only clients with hostnames matching that pattern are returned
    :param sort_ascending: if True - clients are sorted ascending by hostname, descending otherwise
    :return: Monitored clients queryset with filtering and custom sorting applied
    """
    if filter_regex != "":
        filter_regex = re.sub(r"\*", r"[*a-zA-Z0-9-_.]*", filter_regex)
        filter_regex = r"^" + filter_regex + "$"
        clients = Client.objects.filter(hostname__iregex=filter_regex)
    else:
        clients = Client.objects.all()

    return clients.order_by("-hostname" if sort_ascending else "hostname")


def get_monitored_properties(client):
    """
    :param client: client of which monitoring properties should be returned
    :return: queryset of client's monitored properties
    """
    return client.monitored_properties.all()


def remove_client_anystate(pk):
    """
    Remove pending, blocked or monitored client's data
    :param pk:
    :return:
    """
    client = ClientBase.objects.get(pk=pk)
    client.delete()
