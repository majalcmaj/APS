from django.db import models

class ClientBase(models.Model):
    hostname = models.CharField(max_length=200, null=False, unique=True)
    ip_address = models.CharField(max_length=15, null=False, unique=True)

    class Meta:
        abstract = True


class PendingClient(ClientBase):
    pass

class BlockedClient(ClientBase):
    pass

class Client(ClientBase):
    probing_interval = models.IntegerField(default=10)

class MonitoredProperties(models.Model):
    CPU_USAGE="cpu"
    RAM_USAGE="ram"
    DISK_USAGE="dsk"

    MONITORED_PROPERTIES_CHOICES= (
        (CPU_USAGE, 'cpu_usage'),
        (RAM_USAGE, 'ram_usage'),
        (DISK_USAGE, 'disk_usage'),
    )

    monitored_properties = models.CharField(max_length=3, choices=MONITORED_PROPERTIES_CHOICES, null=False)
    client=models.ForeignKey(Client, on_delete=models.CASCADE, null=False)

    @staticmethod
    def get_possible_choices():
        return [el[1] for el in MonitoredProperties.MONITORED_PROPERTIES_CHOICES]



