from acquisition_presentation_server.models import MonitoredProperty, ClientBase
from ..models import PendingClient, Client, BlockedClient
from django.db import IntegrityError, transaction


class ClientsStateManager:
    @staticmethod
    @transaction.atomic
    def register_new_pending_client(client_hostname, client_address, client_port, monitored_properties):

        if len(Client.objects.filter(hostname=client_hostname)) > 0:
            raise ClientsManagerException("Already registered")
        if len(BlockedClient.objects.filter(hostname=client_hostname)) > 0:
            raise ClientsManagerException("Already blocked")
        if len(PendingClient.objects.filter(hostname=client_hostname)) > 0:
            raise ClientsManagerException("Already pending")
        pending_client = PendingClient(
            hostname=client_hostname,
            ip_address=client_address,
            port=client_port,
            state=ClientBase.PENDING
        )
        pending_client.save()
        for monitored_property in monitored_properties.items():
            MonitoredProperty(
                client=pending_client,
                name=monitored_property[0],
                type=monitored_property[1],
            ).save()

    @staticmethod
    @transaction.atomic
    def accept_pending_client(pk):
        pending_client = PendingClient.objects.get(pk=pk)
        pending_client.state = ClientBase.MONITORED
        pending_client.save()

    @staticmethod
    @transaction.atomic
    def block_pending_client(pk):
        pending_client = PendingClient.objects.get(pk=pk)
        pending_client.state = ClientBase.BLOCKED
        pending_client.save()


    @staticmethod
    @transaction.atomic
    def accept_blocked_client(pk):
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
