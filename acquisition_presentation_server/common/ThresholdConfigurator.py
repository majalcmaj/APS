from acquisition_presentation_server.models import Threshold, MonitoredProperty

"""
File containing functions used for manipulating thresholds
"""


def add_threshold(value, cycles, type, mp_pk):
    """
    :param value: Value which generates alert when exceeded
    :param cycles: Received probes above specified value, which have to be collected for the alert to be created
    :param type: Type of action taken of threshold ocurrance
    :param mp_pk: Property public key for which the threshold should be created
    """
    threshold = Threshold(type=type,
                          value=value,
                          max_cycle_above_value=cycles,
                          monitored_property=MonitoredProperty.objects.get(pk=mp_pk))
    threshold.save()


def delete_threshold(threshold_pk):
    """
    Delete simple threshold
    :param threshold_pk: threshold's which should be deleted public key in database
    :raises Threshold.DoesNotExist when no thresgold with given public key exists in database
    """
    Threshold.objects.get(pk=threshold_pk).delete()
