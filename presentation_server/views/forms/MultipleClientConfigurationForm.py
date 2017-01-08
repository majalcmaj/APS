from datetime import timedelta
from django import forms


class MultipleClientConfigurationForm(forms.Form):
    consecutive_probes_sent_count = forms.IntegerField(min_value=1, required=True,
                                                       widget=forms.TextInput())

    monitoring_days = forms.IntegerField(label="Days", min_value=0, required=False,
                                         widget=forms.TextInput(attrs={"style": "width: 50px"}))
    monitoring_hours = forms.IntegerField(label="Hours", min_value=0, required=False,
                                          widget=forms.TextInput(attrs={"style": "width: 50px"}))
    monitoring_minutes = forms.IntegerField(label="Minutes", min_value=0, required=False,
                                            widget=forms.TextInput(attrs={"style": "width: 50px"}))
    monitoring_seconds = forms.IntegerField(label="Seconds", min_value=0, required=False,
                                            widget=forms.TextInput(attrs={"style": "width: 50px"}))

    @classmethod
    def from_client(cls, client):
        td = timedelta(seconds=client.monitoring_timespan)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        initial = {
            "consecutive_probes_sent_count": client.consecutive_probes_sent_count,
            "monitoring_days": td.days,
            "monitoring_hours": hours,
            "monitoring_minutes": minutes,
            "monitoring_seconds": seconds

        }
        return cls(initial=initial)

    def get_monitoring_timespan(self):
        td = timedelta(
            days=self.cleaned_data['monitoring_days'],
            hours=self.cleaned_data['monitoring_hours'],
            minutes=self.cleaned_data['monitoring_minutes'],
            seconds=self.cleaned_data['monitoring_seconds']
        )
        return int(td.total_seconds())
