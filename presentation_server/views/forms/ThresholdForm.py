from django import forms


class ThresholdForm(forms.Form):
    TYPE_CHOICES = ((0, 'Notification'), (1, 'Send e-mail'))
    GT_OR_LT = ('lt', 'Value below trigger'), (('gt', 'Value above trigger'))
    value = forms.IntegerField(min_value=0, label='Threshold Value',
                               widget=forms.TextInput(attrs={"class": "form-control"}))
    gt_or_lt = forms.ChoiceField(label="", choices=GT_OR_LT, widget=forms.Select(attrs={"class": "form-control"}))
    cycles_above = forms.IntegerField(min_value=1, label="Consecutive abnormal probes count",
                                      widget=forms.TextInput(attrs={"class": "form-control"}))
    type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))
    client_pk = forms.IntegerField(widget=forms.HiddenInput())
    message_template = forms.CharField(label="Message template", max_length=500,
                                     widget=forms.Textarea(attrs={"class": "form-control"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["message_template"] = "%(timestamp): There were %(consecutive_abnormal) consecutive abnormal " \
                                         "probes on property %(mp_name) for " \
                                         "host %(client_hostname). Threshold set for %(max_consecutive) consecutive " \
                                         "probes where value %(gt_or_lt) %(threshold_value)."

    @classmethod
    def for_client(cls, client_pk):
        result = cls(initial={"client_pk": client_pk})
        return result
