# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-19 04:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wifiportal', '0009_auto_20180119_0351'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Restaurant',
            new_name='Organization',
        ),
        migrations.RenameField(
            model_name='Customer',
            old_name='restaurant',
            new_name='organization'
        ),
        migrations.RenameField(
            model_name='Commodity',
            old_name='restaurant',
            new_name='organization'
        ),
    ]
