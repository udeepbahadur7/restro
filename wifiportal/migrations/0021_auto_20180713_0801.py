# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-13 08:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wifiportal', '0020_auto_20180615_0528'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotspotconfig',
            name='hotspot_user',
            field=models.CharField(default='user1', max_length=100, verbose_name='Hotspot Username'),
        ),
        migrations.AddField(
            model_name='hotspotconfig',
            name='hotspot_user_password',
            field=models.CharField(default='user1', max_length=100, verbose_name='Hotspot User Password'),
        ),
    ]
