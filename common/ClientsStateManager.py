from acquisition_presentation_server.models import MonitoredProperties
from ..models import PendingClient, Client, BlockedClient
from django.db import IntegrityError


class ClientsStateManager:
    @staticmethod
    def register_new_pending_client(client_hostname, client_address, client_port, monitored_properties):

        if len(Client.objects.filter(hostname=client_hostname)) > 0:
            raise ClientsManagerException("Already registered")
        if len(BlockedClient.objects.filter(hostname=client_hostname)) > 0:
            raise ClientsManagerException("Already blocked")
        if len(PendingClient.objects.filter(hostname=client_hostname)) > 0:
            raise ClientsManagerException("Already pending")
        pending_client = PendingClient(hostname=client_hostname,
                                       ip_address=client_address,
                                       port=client_port)
        pending_client.save()
        for monitored_property in monitored_properties.items():
            mp, _ = MonitoredProperties.objects.get_or_create(name=monitored_property[0],
                                                      type=monitored_property[1])
            pending_client.monitored_properties.add(mp)
        pending_client.save()

    @staticmethod
    def accept_pending_client(pk):
        pending_client = PendingClient.objects.get(pk=pk)
        client = Client(hostname=pending_client.hostname,
                        ip_address=pending_client.ip_address,
                        port=pending_client.port)
        client.save()
        for prop in pending_client.monitored_properties.all():
            client.monitored_properties.add(prop)
        client.save()
        pending_client.delete()

    @staticmethod
    def accept_blocked_client(pk):
        blocked_client = BlockedClient.objects.get(pk=pk)
        client = Client(hostname=blocked_client.hostname,
                        ip_address=blocked_client.ip_address,
                        port=blocked_client.port)
        client.save()
        for prop in blocked_client.monitored_properties.all():
            client.monitored_properties.add(prop)
        client.save()
        blocked_client.delete()

    @staticmethod
    def block_pending_client(pk):
        pending_client = PendingClient.objects.get(pk=pk)
        client = BlockedClient(hostname=pending_client.hostname,
                               ip_address=pending_client.ip_address,
                               port=pending_client.port)
        client.save()
        for prop in pending_client.monitored_properties.all():
            client.monitored_properties.add(prop)
        client.save()
        pending_client.delete()

class ClientsManagerException(BaseException):
    def __init__(self, message=None):
        self._message = "Error durring processing clients" if message is None else message
        super().__init__(self._message)

    @property
    def message(self):
        return self._message