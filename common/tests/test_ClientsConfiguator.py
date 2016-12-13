from django.test import TestCase

from common.libs import ClientsConfigurator
from common.models import Client, ClientBase, MonitoredProperty


class ClientswConfiguratorTestCase(TestCase):

    def test_apply_configuration(self):
        client = self._create_client()
        self.assertEqual(client.is_configured, False, "Is configured should be false")
        new_hostname = "NewHostname"
        new_probing_cycles=100
        new_monitored_pks = list(client.monitored_properties.values_list("pk", flat=True))[0:2]
        new_on_dashboard=new_monitored_pks[0]
        new_monitoring_timespan=3600
        ClientsConfigurator.apply_configuration(
            client.pk,
            new_hostname,
            new_probing_cycles,
            new_monitored_pks,
            new_on_dashboard,
            new_monitoring_timespan
        )
        client= Client.objects.get(pk=client.pk)
        self.assertTrue(client.is_configured, "is_configured flag should be raised")
        self.assertEqual(client.consecutive_probes_sent_count, new_probing_cycles,
                         "Probing cycles be %d"%new_probing_cycles)
        self.assertEqual(client.property_on_dashboard.pk, new_on_dashboard,
                         "Prop on dashboard should be %d"%new_on_dashboard)
        self.assertEqual(client.monitoring_timespan, new_monitoring_timespan,
                         "Monitoring timespan should be %d"%new_monitoring_timespan)
        self.assertListEqual(sorted(list(client.monitored_properties.filter(monitored=True)
                             .values_list("pk", flat=True))),
                             sorted(new_monitored_pks)
                             )

    def test_form_configuration_data(self):
        client = self._create_client()
        mps = list(client.monitored_properties.values_list("pk", flat=True))
        ClientsConfigurator.apply_configuration(
            client.pk,
            client.hostname,
            client.consecutive_probes_sent_count,
            mps,
            mps[0],
            client.monitoring_timespan
        )
        client = Client.objects.get(pk=client.pk)
        data = ClientsConfigurator.form_configuration_data_for_client(client)
        self.assertEqual(data["probing_interval"], client.consecutive_probes_sent_count)
        mps = sorted([cl.name for cl in client.monitored_properties.filter(monitored=True)])
        self.assertListEqual(sorted(data["monitoring_parameters"]), mps)

    def test_form_configuration_data_not_configured(self):
        client = self._create_client()
        mps = list(client.monitored_properties.values_list("pk", flat=True))
        ClientsConfigurator.apply_configuration(
            client.pk,
            client.hostname,
            client.consecutive_probes_sent_count,
            mps,
            mps[0],
            client.monitoring_timespan
        )
        self.assertIsNone(ClientsConfigurator.form_configuration_data_for_client(client))

    def test_ack_configuration_applied(self):
        client = self._create_client()
        mps = list(client.monitored_properties.values_list("pk", flat=True))
        ClientsConfigurator.apply_configuration(
            client.pk,
            client.hostname,
            client.consecutive_probes_sent_count,
            mps,
            mps[0],
            client.monitoring_timespan
        )
        client = Client.objects.get(pk=client.pk)
        self.assertTrue(client.configuration_pending)
        ClientsConfigurator.ack_configuration_applied(client)
        client = Client.objects.get(pk=client.pk)
        self.assertFalse(client.configuration_pending)

    @staticmethod
    def _create_client():
        client = Client(
            hostname="test",
            ip_address="255.255.255.255",
            base_probing_interval=10,
            state=ClientBase.MONITORED
        )
        client.save()
        for monitored_property in {"Test1": "unit1", "Test1": "unit2", "Test1": "unit3"}.items():
            MonitoredProperty(
                client=client,
                name=monitored_property[0],
                type=monitored_property[1],
            ).save()
        return client
