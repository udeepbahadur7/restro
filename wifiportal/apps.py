# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class WifiportalConfig(AppConfig):
    name = 'wifiportal'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Organization'))
        registry.register(self.get_model('Commodity'))
        registry.register(self.get_model('Customer'))
        registry.register(self.get_model('HotspotConfig'))
