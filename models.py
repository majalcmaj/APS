from django.db import models
from django.db.models.fields.related import ManyToManyField

from acquisition_presentation_server import settings


class MonitoredProperties(models.Model):
    name = models.CharField(max_length=20, null=False)
    type = models.CharField(max_length=20, null=False)

    class Meta:
        unique_together = (("name", "type"),)

    def __str__(self):
        return "{} [{}]".format(str(self.name), str(self.type))

class ClientBase(models.Model):
    hostname = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=15, null=False, unique=True)
    port = models.IntegerField(default=13000)
    monitored_properties = ManyToManyField(MonitoredProperties)

    class Meta:
        abstract = True


class PendingClient(ClientBase):
    pass

class BlockedClient(ClientBase):
    pass

class Client(ClientBase):
    probing_interval = models.IntegerField(default=10)
    is_configured = models.BooleanField(default=False)
    @property
    def rrd_database_location(self):
        return settings.RRD_DATABASE_DIRECTORY + "/aps_{}.rrd".format(self.hostname)

    def __str__(self):
        return "Host: {} IP:{} Probing_interval:{} Monitored Properties: [{}]"\
            .format(self.hostname, self.ip_address, self.probing_interval,
                    ', '.join([str(prop) for prop in self.monitored_properties.all()]))

