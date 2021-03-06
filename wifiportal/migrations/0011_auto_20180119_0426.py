# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-19 04:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wifiportal', '0010_auto_20180119_0425'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='cover_image',
            field=models.ImageField(upload_to=b'', verbose_name='Organization Cover Pics'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='location',
            field=models.CharField(max_length=100, verbose_name='Organization Location'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.ImageField(upload_to=b'', verbose_name='Organization Logo'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Organization name'),
        ),
    ]
