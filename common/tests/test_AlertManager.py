from django.test import TestCase

from common.libs import ClientManager
from common.models import Client


class AlertManagerTestCase(TestCase):
    def setUp(self):
        cl1 = Client(
            hostname="Test1",
            ip_address="test"
        )
        cl1.save()
        cl2 = Client(
            hostname="Test2",
            ip_address="test"
        )
        cl2.save()
        cl3 = Client(
            hostname="_Test3",
            ip_address="test"
        )
        cl3.save()
        self._clients = [cl1, cl2, cl3]

    def test_get_all_clients(self):
        all_clients = ClientManager.get_all_clients()
        self.assertEqual(len(self._clients), len(all_clients),
                         "There should be {} clients in db, but there "
                         "were {} of them".format(
                             len(self._clients), len(all_clients)
                         ))
        for cl in self._clients:
            self.assertIn(cl,
                          all_clients,
                          "Client with pk {} should exist in database.".format(cl.pk))

    def test_get_clients(self):
        self.assertEqual(len(ClientManager.get_clients("Test1")), 1,
                         "Specified regex should return 1 client only.")
        self.assertEqual(len(ClientManager.get_clients("Test*")), 2,
                         "Specified regex should return 2 clients only.")
        self.assertEqual(len(ClientManager.get_clients("*error*")), 0,
                         "Specified regex should return no clients.")
        self.assertEqual(len(ClientManager.get_clients("*")), Client.objects.count(),
                         "Specified regex should return all clients.")
        self.assertEqual(len(ClientManager.get_clients("")), Client.objects.count(),
                         "Specified regex should return all clients.")
        self.assertListEqual(list(ClientManager.get_clients(sort_ascending=True)),
                         list(sorted(self._clients,key= lambda cl: cl.hostname, reverse=True)),
                         "Clients are not sorted correctly.")
        self.assertListEqual(list(ClientManager.get_clients("Test*", sort_ascending=True)),
                         list(sorted(self._clients[0:2],key= lambda cl: cl.hostname, reverse=True)),
                         "Clients are not sorted correctly.")
        self.assertListEqual(list(ClientManager.get_clients("*", sort_ascending=False)),
                             list(sorted(self._clients, key=lambda cl: cl.hostname, reverse=False)),
                             "Clients are not sorted correctly.")


