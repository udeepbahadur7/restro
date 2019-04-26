from django import forms

from wifiportal.models import Customer


class MikrotikForm(forms.Form):
    mac = forms.CharField(label='Mac Address', max_length=100, required=False)
    ip = forms.CharField(label='Ip Address', max_length=500, required=False)
    username = forms.CharField(label='username', max_length=90, required=False)
    link_login = forms.CharField(max_length=10000)
    link_orig = forms.CharField(max_length=10000, required=False)
    error = forms.CharField(max_length=5000, required=False)
    chap_id = forms.CharField(max_length=1000, required=False)
    chap_challenge = forms.CharField(max_length=1000, required=False)
    link_login_only = forms.CharField(max_length=10000)
    link_orig_esc = forms.CharField(max_length=10000, required=False)
    mac_esc = forms.CharField(max_length=5000)
    blocked = forms.BooleanField(required=False)

class CustomerForm(forms.ModelForm):
    phone_number = forms.CharField(required=True)
    class Meta:
        model = Customer
        fields = ('name', 'phone_number', 'dob', 'organization', 'deals_subscription', 'user_agent', 'mac_address')
