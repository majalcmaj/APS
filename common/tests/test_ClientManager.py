from django.test import TestCase

from common.libs import AlertManager
from common.models import Client, Alert


class ClientManagerTestCase(TestCase):
    def setUp(self):
        client = Client(
            hostname="Test",
            ip_address="test"
        )
        client.save()
        client2 = Client(
            hostname="Test",
            ip_address="test"
        )
        client2.save()
        alert1 = Alert(message="Test", client=client)
        alert1.save()
        alert2 = Alert(message="Test", client=client)
        alert2.save()
        alert3 = Alert(message="Test", client=client2)
        alert3.save()
        self._alerts = [alert1.pk, alert2.pk]
        self._client = client
        self._client2 = client2

    def test_remove_single(self):
        AlertManager.delete_alert(self._alerts[0])
        with self.assertRaises(expected_exception=Alert.DoesNotExist,
                               msg="Alert not found exception should be raised"):
            Alert.objects.get(pk=self._alerts[0])

    def test_remove_not_existing(self):
        with self.assertRaises(expected_exception=Alert.DoesNotExist,
                               msg="Alert not found exception should be raised"):
            Alert.objects.get(pk=-1)

    def test_remove_all(self):
        self.assertGreater(self._client.alerts.count(), 0,
                           "Test error: Alerts count should be greater than 0")
        AlertManager.delete_all_for_client(self._client.pk)
        self.assertEqual(self._client.alerts.count(), 0,
                         "There should be no alerts left for client")
        self.assertEqual(self._client2.alerts.count(), 1,
                         "Alerts from client other than specified have been deleted too!")