from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminDateWidget
from django.forms import SelectDateWidget
from django.utils.translation import ugettext as _

class DateInput(forms.DateInput):
    input_type = 'date'

class DashboardDateFilterForm(forms.Form):
    timestamp_from = forms.DateTimeField(
        label='Date From',
        widget=DateInput,
        localize=True,
        required=False,
    )
    timestamp_to = forms.DateTimeField(
        label='To',
        widget=DateInput,
        localize=True,
        required=False
    )
