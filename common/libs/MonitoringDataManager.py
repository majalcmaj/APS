import datetime
import logging

from common.libs import RRDtoolManager
from common.libs import EmailMessageManager
from common.models import Threshold, Alert

logger = logging.getLogger("django")

def get_client_data(client, since):
    """
    Get monitoring data of client since provided time
    :param client: client for which the data should be collected
    :param since: unix timestamp(in seconds); time point since when the data from RRD database should be collected
    :return: monitoring data
    """
    return RRDtoolManager.fetch_data(client, since)

def process_data(client, records, timestamp):
    """
    Process data collected from client - save it to rrd database, check for alerts and
    update last_updated timestamp in client entry in db
    :param client: client for which the monitoring data should be processed
    :param records: records containing data deceived from client
    :param timestamp: unix timestamp from client meaning time at which the collected monitoring data on
    client has been sent
    """
    _check_thresholds(client, records)
    RRDtoolManager.update_rrd(client, records, timestamp)
    client.last_update = int(timestamp)
    client.save()


def _check_thresholds(client, records):
    """
    Check if the threshold values are exceeded, based on provided monitoring data from client,
    generate appropriate alert if abnormal client state is detected
    :param client:
    :param records:
    """
    monitored_properties = client.monitored_properties.filter(monitored=True)

    for m in monitored_properties:
        thresholds = m.thresholds.all()
        for t in thresholds:
            if t.is_value_abnormal(records[m.name]):
                t.curr_cons_abnormal_probes += 1
            else:
                t.curr_cons_abnormal_probes = 0

            if t.curr_cons_abnormal_probes >= t.max_cons_abnormal_probes:
                message = _create_message(client, m, t)
                if t.type == Threshold.EMAIL_NOTIFICATION and len(Alert.objects.filter(threshold=t)) == 0:
                    mime_message = EmailMessageManager.create_alert_simple_message(message)
                    EmailMessageManager.send_message(mime_message)

                t.curr_cons_abnormal_probes = 0
                alert = Alert(client=client, threshold=t, message=message)
                alert.save()
            t.save()


def _create_message(client, monitored_prop, threshold):
    """
    Formats alert's message.
    Exchanges words in %() (ex %(timestamp) ) with corresponding values.
    Available exchanges:
    timestamp - time of alert creation
    consecutive_abnormal - current consecutive probes above value count
    consecutive_max - minimal count of consecutive probes exceeding threshold value which
    generate alert
    mp_name - name of monitored property for which the alert is created
    client_hostname - hostname of a client for which the alert is created
    gt_or_lt - type of alert - greater or less; represented by ">" and "<"
    threshold_value - border value for monitored property
    :param client: client for which the alert is created
    :param monitored_prop: monitored property, for which the alert is created
    :param threshold: threshold for alert
    :return: Formatted message
    """
    message = threshold.message_template
    available_tags = (
        ("timestamp", str(datetime.datetime.now())),
        ("consecutive_abnormal", str(threshold.curr_cons_abnormal_probes)),
        ("max_consecutive", str(threshold.max_cons_abnormal_probes)),
        ("mp_name", "{} [{}]".format(monitored_prop.name, monitored_prop.type)),
        ("client_hostname", client.hostname),
        ("gt_or_lt", ">" if threshold.is_gt else "<"),
        ("threshold_value", threshold.value),
    )

    for tag in available_tags:
        message = message.replace("%({})".format(tag[0]), str(tag[1]))

    return message