# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

mac_address_validator = RegexValidator(
    regex=r'(?:(?:[0-9a-fA-F]){2}:){5}(?:[0-9a-fA-F]){2}',
    message="Invalid mac address"
)


class Router(models.Model):
    mac_address = models.CharField('Router Mac Address', max_length=17, validators=[mac_address_validator], unique=True)
    nasid = models.CharField('Router Name', max_length=1000)

    def __str__(self):
        return self.nasid

    def __unicode__(self):
        return self.__str__()


class StatusLog(models.Model):
    router = models.ForeignKey(Router, on_delete=models.DO_NOTHING, verbose_name="Router")
    system_time = models.TimeField('Router Time')
    uptime = models.DurationField('Router Uptime')
    load_average = models.FloatField('Average Router Load %')
    entry_timestamp = models.DateTimeField('Status Log Entry Time', default=timezone.now)


