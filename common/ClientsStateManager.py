
from ..models import PendingClient, Client, BlockedClient
from django.db import IntegrityError


class ClientsStateManager:
    @staticmethod
    def register_new_pending_client(client_hostname, client_address):

        if len(Client.objects.filter(hostname=client_hostname)) > 0:
            raise ClientsManagerException("Already registered")
        if len(BlockedClient.objects.filter(hostname=client_hostname)) > 0:
            raise ClientsManagerException("Already blocked")
        if len(PendingClient.objects.filter(hostname=client_hostname)) > 0:
            raise ClientsManagerException("Already pending")
        pending_client = PendingClient(hostname=client_hostname, ip_address=client_address)
        pending_client.save()

    @staticmethod
    def accept_pending_client(pk):
        pending_client = PendingClient.objects.get(pk=pk)
        client = Client(hostname=pending_client.hostname,
                               ip_address=pending_client.ip_address)
        client.save()
        pending_client.delete()

    @staticmethod
    def accept_blocked_client(pk):
        blocked_client = BlockedClient.objects.get(pk=pk)
        client = Client(hostname=blocked_client.hostname,
                        ip_address=blocked_client.ip_address)
        client.save()
        blocked_client.delete()

    @staticmethod
    def block_pending_client(pk):
        pending_client = PendingClient.objects.get(pk=pk)
        client = BlockedClient(hostname=pending_client.hostname,
                               ip_address=pending_client.ip_address)
        client.save()
        pending_client.delete()

class ClientsManagerException(BaseException):
    def __init__(self, message=None):
        self._message = "Error durring processing clients" if message is None else message
        super().__init__(self._mesage)

    @property
    def message(self):
        return self._message