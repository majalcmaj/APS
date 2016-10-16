from django.db import models
from django.db.models.fields.related import ManyToManyField


class ClientBase(models.Model):
    hostname = models.CharField(max_length=200, null=False, unique=True)
    ip_address = models.CharField(max_length=15, null=False, unique=True)

    class Meta:
        abstract = True


class PendingClient(ClientBase):
    pass

class BlockedClient(ClientBase):
    pass

class MonitoredProperties(models.Model):
    CPU_USAGE="cpu"
    RAM_USAGE="ram"
    DISK_USAGE="dsk"

    MONITORED_PROPERTIES_CHOICES= (
        (CPU_USAGE, 'cpu_usage'),
        (RAM_USAGE, 'ram_usage'),
        (DISK_USAGE, 'disk_usage'),
    )

    property_name = models.CharField(max_length=3, choices=MONITORED_PROPERTIES_CHOICES, null=False)
    @staticmethod
    def get_possible_choices():
        return [el[1] for el in MonitoredProperties.MONITORED_PROPERTIES_CHOICES]

    def __str__(self):
        return str(self.property_name)

class Client(ClientBase):
    probing_interval = models.IntegerField(default=10)
    monitored_properties = ManyToManyField(MonitoredProperties)

    def __str__(self):
        return "Host: {} IP:{} Probing_interval:{} Monitored Properties: [{}]"\
            .format(self.hostname, self.ip_address, self.probing_interval,
                    ', '.join([str(prop) for prop in self.monitored_properties.all()]))



