import logging

from acquisition_presentation_server.models import MonitoredProperty, Threshold, Alert
from acquisition_presentation_server.common.RRDtoolManager import RRDtoolManager
import time
from django.db import transaction
from acquisition_presentation_server.common.EmailMessageManager import EmailMessageManager

logger = logging.getLogger("django")


class ManageMonitoringData:
    @staticmethod
    def process_data(client, records):
        print(records)
        ManageMonitoringData._check_thresholds(client, records)
        RRDtoolManager(client).update_rrd(records)
        client.last_update = int(time.time())
        client.save()

    @staticmethod
    @transaction.atomic
    def _check_thresholds(client, records):
        monitored_properties = MonitoredProperty.objects.filter(client=client, monitored=True)

        for m in monitored_properties:
            thresholds = Threshold.objects.filter(monitored_property=m)
            for t in thresholds:
                print(m.name, t.value, t.cycles_above_value, t.max_cycle_above_value)
                if float(records[m.name]) > t.value:
                    t.cycles_above_value += 1
                else:
                    t.cycles_above_value = 0

                if t.cycles_above_value == t.max_cycle_above_value:
                    message = "Client (id = {}) reached {} value above {}".format(client.pk, m.name, t.value)
                    if t.type == Threshold.EMAIL_NOTIFICATION and len(Alert.objects.filter(threshold=t)) == 0:
                        mime_message = EmailMessageManager.create_alert_simple_message(message)
                        EmailMessageManager.send_message(mime_message)

                    t.cycles_above_value = 0
                    alert = Alert(client=client, threshold=t, message=message)
                    alert.save()
                t.save()

        alerts = Alert.objects.all()
        for alert in alerts:
            print(alert.message)
