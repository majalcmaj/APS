from common.models import MonitoredProperty, ClientBase, PendingClient, BlockedClient

"""
File contains functions which take care of registering new pending client and
altering client states, which are PENDING(newly registered), MONITORED (machine is
accepted to the system and its properties are monitored) and BLOCKED (machine has been
excluded from monitoring)
"""
def register_new_pending_client(client_hostname, client_address, monitored_properties,
                                base_probing_interval):
    """
    Registers client as pending, based on info sent in initial message
    :param client_hostname: Hostname of client being registered
    :param client_address: IP from which the client request has come
    :param monitored_properties: List of properties which client is able to monitor with units.
    :param base_probing_interval: interval between two consecutive probes on client's side
    :return: public key of client in database
    """
    pending_client = PendingClient(
        hostname=client_hostname,
        ip_address=client_address,
        base_probing_interval=base_probing_interval,
        state=ClientBase.PENDING,
    )
    pending_client.save()
    for monitored_property in monitored_properties.items():
        MonitoredProperty(
            client=pending_client,
            name=monitored_property[0],
            type=monitored_property[1],
        ).save()
    return pending_client.pk


def accept_pending_client(pk):
    """
    Alter pending client's state to MONITORED
    :param pk: client's pk
    """
    pending_client = PendingClient.objects.get(pk=pk)
    pending_client.state = ClientBase.MONITORED
    pending_client.save()


def block_pending_client(pk):
    """
    Alter pending client's state to BLOCKED
    :param pk: client's pk
    """
    pending_client = PendingClient.objects.get(pk=pk)
    pending_client.state = ClientBase.BLOCKED
    pending_client.save()


def accept_blocked_client(pk):
    """
    Alter blocked client's state to MONITORED
    :param pk: client's pk
    """
    pending_client = BlockedClient.objects.get(pk=pk)
    pending_client.state = ClientBase.MONITORED
    pending_client.save()


class ClientsManagerException(BaseException):
    def __init__(self, message=None):
        self._message = "Error durring processing clients" if message is None else message
        super().__init__(self._message)

    @property
    def message(self):
        return self._message
