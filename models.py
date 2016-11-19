from django.db import models
from django.db.models.fields.related import ManyToManyField

from DjangoSites import settings


class ClientBase(models.Model):
    PENDING = 0
    MONITORED = 1
    BLOCKED = 2

    hostname = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=15, null=False)
    port = models.IntegerField(default=13000)
    probing_interval = models.IntegerField(default=10)
    is_configured = models.BooleanField(default=False)
    last_update = models.IntegerField(default=-1)
    state = models.IntegerField(default=PENDING, db_index=True)
    property_on_dashboard = models.ForeignKey("MonitoredProperty", on_delete=models.DO_NOTHING, null=True)
    configuration_pending = models.BooleanField(default=True)
    base_probing_interval = models.IntegerField(default=1)

    @property
    def rrd_database_location(self):
        return settings.RRD_DATABASE_DIRECTORY + "/aps_{}.rrd".format(self.hostname)

    def __str__(self):
        return "Host: {} IP:{} Probing_interval:{} Monitored Properties: [{}]" \
            .format(self.hostname, self.ip_address, self.probing_interval,
                    ', '.join([str(prop) for prop in self.monitored_properties.all()]))


class MonitoredProperty(models.Model):
    name = models.CharField(max_length=20, null=False)
    type = models.CharField(max_length=20, null=False)
    monitored = models.BooleanField(default=True)
    client = models.ForeignKey(ClientBase, on_delete=models.CASCADE, related_name="monitored_properties")

    def __str__(self):
        return "{} [{}]".format(str(self.name), str(self.type))


class Threshold(models.Model):
    WARNING = 0
    EMAIL_NOTIFICATION = 1

    type = models.IntegerField(default=WARNING)
    value = models.IntegerField()
    cycles_above_value = models.IntegerField(default=0)
    max_cycle_above_value = models.IntegerField(default=1)
    monitored_property = models.ForeignKey(MonitoredProperty, on_delete=models.CASCADE, related_name="thresholds")

    def type_as_string(self):
        return "Warning" if self.type == 0 else "e-mail notification"

class Alert(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    client = models.ForeignKey(ClientBase, on_delete=models.CASCADE, related_name="alerts")
    threshold = models.ForeignKey(Threshold, on_delete=models.DO_NOTHING, related_name="alerts")


class Client(ClientBase):
    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(state=ClientBase.MONITORED)

    objects = Manager()

    class Meta:
        proxy = True

    def has_alerts(self):
        return self.alerts.count() > 0


class PendingClient(ClientBase):
    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(state=ClientBase.PENDING)

    objects = Manager()

    class Meta:
        proxy = True


class BlockedClient(ClientBase):
    class Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(state=ClientBase.BLOCKED)

    objects = Manager()

    class Meta:
        proxy = True
