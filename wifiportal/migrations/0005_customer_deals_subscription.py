# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-11 06:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wifiportal', '0004_auto_20180109_0548'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='deals_subscription',
            field=models.BooleanField(default=True, verbose_name='Subscribe for the deals'),
        ),
    ]
