from acquisition_presentation_server.models import MonitoredProperty, ClientBase, PendingClient, Client, BlockedClient


def register_new_pending_client(client_hostname, client_address, monitored_properties,
                                base_probing_interval):
    # TODO Rozrozniac przychodzace klienty
    # if len(Client.objects.filter(hostname=client_hostname)) > 0:
    #     raise ClientsManagerException("Already registered")
    # if len(BlockedClient.objects.filter(hostname=client_hostname)) > 0:
    #     raise ClientsManagerException("Already blocked")
    # if len(PendingClient.objects.filter(hostname=client_hostname)) > 0:
    #     raise ClientsManagerException("Already pending")
    prop_on_dashboard = None

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
    pending_client = PendingClient.objects.get(pk=pk)
    pending_client.state = ClientBase.MONITORED
    pending_client.save()


def block_pending_client(pk):
    pending_client = PendingClient.objects.get(pk=pk)
    pending_client.state = ClientBase.BLOCKED
    pending_client.save()


def accept_blocked_client(pk):
    pending_client = BlockedClient.objects.get(pk=pk)
    pending_client.state = ClientBase.MONITORED
    pending_client.save()


def get_client(pk):
    try:
        return ClientBase.objects.get(pk=pk)
    except ClientBase.DoesNotExist:
        return None

def remove_client(pk):
    client = Client.objects.get(pk=pk)
    client.delete()


class ClientsManagerException(BaseException):
    def __init__(self, message=None):
        self._message = "Error durring processing clients" if message is None else message
        super().__init__(self._message)

    @property
    def message(self):
        return self._message
