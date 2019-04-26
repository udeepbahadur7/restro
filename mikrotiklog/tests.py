# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import SuspiciousOperation
from django.http import HttpRequest
from django.test import TestCase

# Create your tests here.
from django.urls import resolve

from mikrotiklog.models import StatusLog, Router
from mikrotiklog.views import router_status


class RouterStatusLogTest(TestCase):
    def setUp(self):
        router = Router(
            mac_address='AA:BB:CC:DD:EE:FF',
            nasid="TestRouter"
        )
        router.save()
    def tearDown(self):
        pass

    def test_url_resolves_to_view(self):
        found = resolve('/routerlog/status/')
        self.assertEqual(found.func, router_status)

    def test_bad_request_on_normal_get_client(self):
        response = self.client.get('/routerlog/status/')
        response_html = response.content.decode('utf-8')
        self.assertIn('Bad Request', response_html)

    def test_bad_request_not_saved_to_database(self):
        response = self.client.get('/routerlog/status/')
        self.assertEqual(StatusLog.objects.all().count(), 0)

    def test_status_form_invalid_logic(self):
        response = self.client.get('/routerlog/status/',
                                   data=dict(mac_address="AA:BB:CC:DD:EE:FF", nasid="TestRouter", os_date="Mikrotik",
                                             system_time="11:22:45", load_average=90))
        self.assertEqual(response.status_code, 400)

    def test_valid_request_status_code(self):
        response = self.client.get('/routerlog/status/', data=dict(mac_address="AA:BB:CC:DD:EE:FF", nasid="TestRouter", os_date="Mikrotik", system_time="11:22:45", uptime="1w25d00:13:34", load_average=90))
        self.assertEqual(response.status_code, 204)
