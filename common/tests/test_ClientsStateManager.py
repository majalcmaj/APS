from django.test import TestCase

from common.libs import ClientsConfigurator, ClientsStateManager
from common.models import Client, ClientBase, MonitoredProperty, PendingClient


class ClientsStateManager(TestCase):

    def test_register_new_pending_client(self):
        hostname = "Test"
        ip_addres = "123.123.123.123"
        mps = [("prop1", "unit1"), ("prop2", "unit2"), ("prop3", "unit3"), ("prop4", "unit4")]
        base_interval = 100
        pk = ClientsStateManager.register_new_pending_client(
            hostname,
            ip_addres,
            mps,
            base_interval
        )

        client = PendingClient.objects.get(pk=pk)
        self.assertEqual(client.hostname, hostname)
        self.assertEqual(client.ip_address, ip_addres)
        self.assertEqual(client.base_probing_interval, base_interval)
        self.assertEqual(client.monitored_properties.count(), len(mps),
                         "Inserted and database-existing monitored properties differ in count.")
        for prop in client.monitored_properties:
            self.assertIn((prop.name, prop.type), mps,
                          "Monitored property data does not exist in database!")
