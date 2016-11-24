from common.models import Threshold, MonitoredProperty

"""
File containing functions used for manipulating thresholds
"""


def add_threshold(value, cycles, type, mp_pk, is_gt, message_template):
    """
    :param value: Value which generates alert when exceeded
    :param cycles: Received probes above specified value, which have to be collected for the alert to be created
    :param type: Type of action taken of threshold ocurrance
    :param is_gt: If true, alert on value greater than border value, less else
    :param message_template: Template of message to create
    :param mp_pk: Property public key for which the threshold should be created
    """
    threshold = Threshold(type=type,
                          value=value,
                          max_cons_abnormal_probes=cycles,
                          monitored_property=MonitoredProperty.objects.get(pk=mp_pk),
                          is_gt=is_gt,
                          message_template=message_template
    )
    threshold.save()


def delete_threshold(threshold_pk):
    """
    Delete simple threshold
    :param threshold_pk: threshold's which should be deleted public key in database
    :raises Threshold.DoesNotExist when no thresgold with given public key exists in database
    """
    Threshold.objects.get(pk=threshold_pk).delete()
