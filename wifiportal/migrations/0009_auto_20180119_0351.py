# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-19 03:51
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wifiportal', '0008_auto_20180114_1045'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MenuItem',
            new_name='Commodity',
        ),
        migrations.AlterModelOptions(
            name='commodity',
            options={'permissions': (('alter_all_menu_items', 'Can alter all menu items'),), 'verbose_name': 'promotion', 'verbose_name_plural': 'promotions'},
        ),
        migrations.AlterField(
            model_name='customer',
            name='mac_address',
            field=models.CharField(blank=True, max_length=17, null=True, validators=[django.core.validators.RegexValidator(message='Invalid mac address', regex='(?:(?:[0-9a-fA-F]){2}:){5}(?:[0-9a-fA-F]){2}')], verbose_name='Customer Mac Address'),
        ),
    ]