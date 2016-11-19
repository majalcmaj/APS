import logging

from acquisition_presentation_server.common import RRDtoolManager
from acquisition_presentation_server.common import EmailMessageManager
from acquisition_presentation_server.models import Threshold, Alert

logger = logging.getLogger("django")


def process_data(client, records, timestamp):
    _check_thresholds(client, records)
    RRDtoolManager.update_rrd(client, records, timestamp)
    client.last_update = int(timestamp)
    client.save()


def _check_thresholds(client, records):
    monitored_properties = client.monitored_properties.filter(monitored=True)

    for m in monitored_properties:
        thresholds = m.thresholds.all()
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

    # alerts = Alert.objects.all()
    # for alert in alerts:
    #     print(alert.message)
