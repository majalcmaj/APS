from django.db import models

from APS import settings


class ClientBase(models.Model):
    PENDING = 0
    MONITORED = 1
    BLOCKED = 2

    hostname = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=15, null=False)
    monitoring_timespan = models.IntegerField(default=24 * 60 * 60)
    is_configured = models.BooleanField(default=False)
    last_update = models.IntegerField(default=-1)
    state = models.IntegerField(default=PENDING, db_index=True)
    property_on_dashboard = models.ForeignKey("MonitoredProperty", on_delete=models.DO_NOTHING, null=True)
    configuration_pending = models.BooleanField(default=True)
    consecutive_probes_sent_count = models.IntegerField(default=1)
    base_probing_interval = models.IntegerField(default=1)

    def __str__(self):
        return "Host: {} IP:{} Probing_interval:{} Monitored Properties: [{}]" \
            .format(self.hostname, self.ip_address, self.consecutive_probes_sent_count,
                    ', '.join([str(prop) for prop in self.monitored_properties.all()]))


class MonitoredProperty(models.Model):
    name = models.CharField(max_length=20, null=False)
    type = models.CharField(max_length=20, null=False)
    monitored = models.BooleanField(default=True)
    client = models.ForeignKey(ClientBase, on_delete=models.CASCADE, related_name="monitored_properties")

    def is_on_dashboard(self):
        prop_on_dashboard = self.client.property_on_dashboard
        return prop_on_dashboard.pk == self.pk if prop_on_dashboard is not None else False

    class Meta:
        ordering=['name']

    def __str__(self):
        return "{} [{}]".format(str(self.name), str(self.type))


class Threshold(models.Model):
    WARNING = 0
    EMAIL_NOTIFICATION = 1

    type = models.IntegerField(default=WARNING)
    value = models.IntegerField()
    curr_cons_abnormal_probes = models.IntegerField(default=0)
    max_cons_abnormal_probes = models.IntegerField(default=1)
    monitored_property = models.ForeignKey(MonitoredProperty, on_delete=models.CASCADE, related_name="thresholds")
    message_template = models.CharField(max_length=500)
    is_gt = models.BooleanField(default=True)

    def type_as_string(self):
        return "create warning" if self.type == 0 else "send e-mail notification"

    def is_value_abnormal(self, value):
        value = float(value)
        if self.is_gt:
            return value > self.value
        else:
            return value < self.value

    def is_gt_as_string(self):
        return ">" if self.is_gt else "<"


class Alert(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=500)
    client = models.ForeignKey(ClientBase, on_delete=models.CASCADE, related_name="alerts")
    threshold = models.ForeignKey(Threshold, on_delete=models.DO_NOTHING, related_name="alerts", null=True)


class Client(ClientBase):
    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(state=ClientBase.MONITORED)

    objects = Manager()

    class Meta:
        proxy = True

    def has_alerts(self):
        return self.alerts.count() > 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = self.MONITORED


class PendingClient(ClientBase):
    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(state=ClientBase.PENDING)

    objects = Manager()

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = self.PENDING


class BlockedClient(ClientBase):
    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(state=ClientBase.BLOCKED)

    objects = Manager()

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = self.BLOCKED
