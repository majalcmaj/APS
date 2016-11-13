from django import forms


class ClientConfigurationForm(forms.Form):
    hostname = forms.CharField(max_length=30, required=True, label="Hostname")
    ip_port = forms.CharField(label="Client IP", disabled=True, required=False)
    base_probing_interval = forms.CharField(disabled=True,required=False)
    probing_cycles = forms.IntegerField(min_value=1, required=True)

    #monitored_properties = forms.MultipleChoiceField(choices=[])
    #
    # def __init__(self, monitored_properties, *args, **kwargs):
    #     super().__init__(args, kwargs)
    #     self.fields["monitored_properties"] = forms.MultipleChoiceField(
    #         choices=[(p.pk, str(p)) for p in monitored_properties]
    #     )

    @classmethod
    def from_client(cls, client):
        monitored_properties = list(client.monitored_properties.all())
        initial = {
            "hostname": client.hostname,
            "ip_port": "{}:{}".format(client.ip_address, client.port),
            "base_probing_interval": client.base_probing_interval,
            "probing_cycles": client.probing_interval,
            #"monitored_properties": [mp.pk for mp in client.monitored_properties.filter(monitored=True)]
        }
        return cls(initial=initial)


        # self.hostname = client.hostname
        # self.ip_address = client.ip_address
        # self.port = client.port
        # self.probing_interval = client.probing_interval
        # property_choices = ((prop.pk, prop.name) for prop in client.monitored_properties.all())
        # self.monitored_properties.choices = property_choices
        # self.initial = {'monitored_properties':
        #                      [prop.name for prop in client.monitored_properties.filter(monitored=True)]}
        # self.hostname.initial = client.hostname
        # self.ip_address.initial = client.ip_address
        # self.port.initial = client.port
        # self.probing_interval.initial = client.probing_interval
