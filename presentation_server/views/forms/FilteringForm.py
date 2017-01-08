import re

from django import forms
from django.core.exceptions import ValidationError


def validate_simple_regex(value):
    if re.match(r"^[*a-zA-Z0-9-_.]+$", value) is None:
        raise ValidationError(
            'Regex text should conform to \'^[*a-zA-Z0-9-_.]+$\''
        )


class FilteringForm(forms.Form):
    SORT_CHOICES = (
        ("h_asc", 'Hostname ascending'),
        ("h_des", 'Hostname descending')
    )
    filter_regex = forms.CharField(validators=[validate_simple_regex], required=False)
    sorting = forms.ChoiceField(choices=SORT_CHOICES, widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial["sorting"] = "h_asc"
