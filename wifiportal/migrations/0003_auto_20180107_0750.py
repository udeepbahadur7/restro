# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-07 07:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wifiportal', '0002_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='rank',
            field=models.IntegerField(default=1, verbose_name='Item Rank'),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='featured',
            field=models.BooleanField(default=True, verbose_name='Featured Item'),
        ),
    ]
