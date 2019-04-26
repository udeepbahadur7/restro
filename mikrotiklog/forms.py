from locale import format

from django import forms
from django.core.exceptions import ValidationError

from mikrotiklog import models as MTModels


class RouterForm(forms.ModelForm):
    class Meta:
        model = MTModels.Router
        fields = '__all__'


class MikrotikDurationField(forms.DurationField):
    def to_python(self, value):
        try:
            import re, datetime
            pattern = re.compile(
                "((?P<weeks>\d*)w)?((?P<days>\d*)d)?(?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})")
            match = pattern.match(value)

            if not match:
                raise ValidationError("Uptime should be in format wwddhh:mm:ss")

            weeks = match.group('weeks')
            weeks = int(weeks) if weeks else 0
            days = match.group('days')
            days = int(days) if days else 0

            hours = int(match.group('hours'))
            minutes = int(match.group('minutes'))
            seconds = int(match.group('seconds'))

            uptime = datetime.timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)
        except Exception:
            return super(MikrotikDurationField, self).to_python(value)
        return super(MikrotikDurationField, self).to_python(uptime)


class RouterStatusForm(forms.ModelForm):
    uptime = MikrotikDurationField("Router uptime")
    class Meta:
        model = MTModels.StatusLog
        fields = '__all__'
        exclude = ('entry_timestamp', )
