from acquisition_presentation_server.models import Threshold, MonitoredProperty


def add_threshold(value,cycles, type, mp_pk):
    threshold = Threshold(type=type,
                          value=value,
                          max_cycle_above_value=cycles,
                          monitored_property=MonitoredProperty.objects.get(pk=mp_pk))
    threshold.save()

def delete_threshold(threshold_pk):
    Threshold.objects.get(pk=threshold_pk).delete()
