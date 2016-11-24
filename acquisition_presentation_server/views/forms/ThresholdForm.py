from django import forms


class ThresholdForm(forms.Form):
    TYPE_CHOICES = ((0, 'Notification'), (1, 'Send e-mail'))
    value = forms.IntegerField(min_value=0, label='Threshold Value',
                               widget=forms.TextInput(attrs={"class":"form-control"}))
    cycles_above = forms.IntegerField(min_value=1, label="Cycles above value",
                                      widget=forms.TextInput(attrs={"class": "form-control"}))
    type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))
    client_pk = forms.IntegerField(widget=forms.HiddenInput())

    @classmethod
    def for_client(cls, client_pk):
        result = cls(initial={"client_pk":client_pk})
        return result
