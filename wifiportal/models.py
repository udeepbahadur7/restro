# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.conf import settings
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.http.response import Http404
from django.utils import timezone
from easy_thumbnails.fields import ThumbnailerImageField


TIMEZONE_CHOICES = (
    ('Asia/Kathmandu', 'Asia/Kathmandu'),
    ('Asia/Dubai', 'Asia/Dubai'),
)


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Organization name', max_length=50)
    location = models.CharField('Organization Location', max_length=100)
    cover_image = models.ImageField('Organization Cover Pics')
    logo = ThumbnailerImageField('Organization Logo', resize_source=dict(size=(512, 512)))
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,)
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default='Asia/Kathmandu')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.__str__()


class CommodityManager(models.Manager):
    def get_featured_items(self, organization_id):
        return self.filter(
            organization=organization_id,
            featured=True
        ).order_by('rank')[:10]


class Commodity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Item Name', max_length=50)
    description = models.CharField('Item Desctiption', max_length=500)
    image = ThumbnailerImageField('Item Photo', resize_source=dict(size=(500, 500)))
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    featured = models.BooleanField('Featured Item', default=True)
    rank = models.IntegerField('Item Rank', default=1)

    objects = CommodityManager()

    class Meta:
        permissions = (
            ("alter_all_menu_items", "Can alter all menu items"),
        )
        verbose_name = 'promotion'
        verbose_name_plural = 'promotions'


    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.__str__()


class CustomerManager(models.Manager):
    def get_customer(self, mac_address, organization_id):
        try:
            return self.filter(mac_address=mac_address, organization_id=organization_id).first()
        except:
            return None

    def get_new_customer_counts(self, from_date, to_date, user):
        if not user.is_staff:
            raise PermissionDenied

        filter_items = dict(entry_timestamp__gt=from_date, entry_timestamp__lt=to_date)
        if not user.is_superuser:
            if not hasattr(user, 'organization'):
                raise SuspiciousOperation('User has no organization.')
            filter_items['organization'] = user.organization

        return self.filter(**filter_items)\
            .annotate(day=TruncDay('entry_timestamp'))\
            .values('day', 'organization_id')\
            .annotate(count=Count('day'))\
            .values('day', 'organization_id', 'organization__name', 'count')\
            .order_by('day')


class Customer(models.Model):
    name = models.CharField('Customer Name', max_length=50)
    phone_number = models.CharField('Customer Phone Number', max_length=20,
                                    validators=[RegexValidator(
                                        regex=r'^(?:05|9\d)\d{8}$',
                                        message="Invalid Phone Number!!! Please enter valid 10 digit phone number")],
                                    blank=True, null=True
                                    )
    dob = models.DateField('Customer Date of Birth', blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    deals_subscription = models.BooleanField("Subscribe for the deals", default=True)
    mac_address = models.CharField('Customer Mac Address', max_length=17,
                                   validators=[RegexValidator(
                                       regex=r'(?:(?:[0-9a-fA-F]){2}:){5}(?:[0-9a-fA-F]){2}',
                                       message="Invalid mac address"
                                   )], blank=True, null=True)
    user_agent = models.CharField(max_length=1000, blank=True, null=True)
    entry_timestamp = models.DateTimeField('Customer Entry Time', default=timezone.now)
    last_login_timestamp = models.DateTimeField('Customer Entry Time', blank=True, null=True)
    blocked = models.BooleanField('Block this person', default=False)
    objects = CustomerManager()

    class Meta:
        permissions = (
            ("alter_all_customer_data", "Can alter all customer data"),
        )

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.__str__()


class HotspotConfig(models.Model):
    enable_advertisement_image = models.BooleanField(default=False)
    advertisement_image = ThumbnailerImageField(
        'Advertisement Image',
        resize_source=dict(size=(512, 512)),
        null=True,
        blank=True
    )
    enable_password = models.BooleanField("Enable Password on hotspot page", default=False)
    password = models.CharField("Password for hotspot", max_length=100, blank=True, null=True)
    password_changed_timestamp = models.DateTimeField('Password Changed on', default=timezone.now)

    login_redirect_page = models.CharField("Redirect to this page after hotspot login", blank=True, null=True, max_length=5000)
    organization = models.OneToOneField(Organization, on_delete=models.PROTECT)

    hotspot_user = models.CharField('Hotspot Username', default='user1', max_length=100)
    hotspot_user_password = models.CharField('Hotspot User Password', default='user1', max_length=100)

    class Meta:
        permissions = (
            ("alter_all_hotspot_config", "Can alter all hotspot configs"),
            ("manage_hotspot_password", "Can manage own hotspot password"),
            ("can_add_advertisement_image", "Can add advertisement image"),
        )

    def is_hotspot_password_valid(self, password_input):
        return self.password == password_input