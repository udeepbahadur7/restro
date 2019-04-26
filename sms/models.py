from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from wifiportal.models import Customer, Organization


SMS_STATUS_CHOICES = (
    ('PENDING', 'PENDING'),
    ('SUCCESS', 'SUCCESS'),
    ('FAILED', 'FAILED'),
)

SMS_GATEWAY_CHOICES = (
    ('SPARROW_SMS', 'SPARROW_SMS'),
)

MAX_RETRY_COUNT = 10


class SMS(models.Model):
    message = models.CharField(_('SMS Message'), max_length=160)
    recipient = models.ManyToManyField(Customer, through='CustomerSMS', through_fields=('sms', 'receiver'))
    scheduled_timestamp = models.DateTimeField(_('Send SMS on'), default=timezone.now)
    creation_timestamp = models.DateTimeField(_('Creation Time'), default=timezone.now)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    payment_received = models.BooleanField('Payment', default=False)

    class Meta:
        permissions = (
            ("alter_all_SMS", "Can alter all SMS"),
        )
        verbose_name_plural = 'SMS'

    def __str__(self):
        return self.message

    def __unicode__(self):
        return self.__str__()


class CustomerSMS(models.Model):
    receiver = models.ForeignKey(Customer, on_delete=models.PROTECT)
    sms = models.ForeignKey(SMS, on_delete=models.PROTECT)
    status = models.CharField('SMS Status', max_length=50, choices=SMS_STATUS_CHOICES, default='PENDING')
    status_detail = models.CharField('SMS Status detail', max_length=10000, blank=True, null=True)
    sms_gateway = models.CharField('SMS Gateway', max_length=50, choices=SMS_GATEWAY_CHOICES)

    class Meta:
        permissions = (
            ("alter_all_CustomerSMS", "Can alter all Customer SMS"),
        )
        verbose_name_plural = 'CustomerSMS'

    def __str__(self):
        return self.receiver.name

    def __unicode__(self):
        return self.__str__()