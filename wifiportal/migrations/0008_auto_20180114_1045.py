# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-14 10:45
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wifiportal', '0007_auto_20180114_0737'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='mac_address',
            field=models.CharField(blank=True, max_length=17, null=True, validators=[django.core.validators.RegexValidator(message='Invalid mac address', regex='(?:(?:[0-9a-eA-E]){2}:){5}(?:[0-9a-eA-E]){2}')], verbose_name='Customer Mac Address'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='user_agent',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
