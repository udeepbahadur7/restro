# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-13 07:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0001_squashed_0007_remove_customersms_retry_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='sms',
            name='payment_received',
            field=models.BooleanField(default=False, verbose_name=b'Payment'),
        ),
    ]
