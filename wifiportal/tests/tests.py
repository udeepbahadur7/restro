# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import shutil
import tempfile

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase, override_settings

from django.urls import reverse
from io import BytesIO

from functional_tests import get_temporary_image
from wifiportal.models import Organization, Customer

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class HotspotPromotionPageTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='test', email='email@helo.com', password='testpassword')
        user.save()

        org = Organization(
            id='d773b604-2457-4b0a-b224-555555555555',
            name='Test Org',
            location='test',
            cover_image=get_temporary_image(),
            logo=get_temporary_image(),
            owner= user
        )
        org.save()

    def tearDown(self):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def test_hotspot_page_get_access_returns_400(self):
        response = self.client.get(reverse('wifiportal:hotspotView', kwargs=dict(organization_id='d773b604-2457-4b0a-b224-3ab672439a57')))
        self.assertEqual(response.status_code, 400)

    def test_hotspot_page_invalid_organization_returns_404_request(self):
        response = self.client.post(reverse('wifiportal:hotspotView', kwargs=dict(organization_id='d773b604-2457-4b0a-b224-3ab672439a57')))
        self.assertEqual(response.status_code, 404)

    def test_invalid_mac_address_hotspot_page(self):
        response = self.client.post(
            reverse('wifiportal:hotspotView', kwargs=dict(organization_id='d773b604-2457-4b0a-b224-555555555555')),
            data=dict(
                link_login='http://lkdsfkldfajlkfjalkfankflkaslfa.com.ds/dsfalklsejowr/ewrwrlkl',
                link_login_only='http://lkdsfkldfajlkfjalkfankflkaslfa.com.ds/dsfalklsejowr/ewrwrlkl',
              )
        )

        self.assertEqual(response.status_code, 400)

    def test_valid_hotspot_page(self):
        response = self.client.post(
            reverse('wifiportal:hotspotView', kwargs=dict(organization_id='d773b604-2457-4b0a-b224-555555555555')),
            data=dict(
                mac='22:22:22:22:22:22',
                link_login='http://lkdsfkldfajlkfjalkfankflkaslfa.com.ds/dsfalklsejowr/ewrwrlkl',
                link_login_only='http://lkdsfkldfajlkfjalkfankflkaslfa.com.ds/dsfalklsejowr/ewrwrlkl',
                mac_esc="22:22:22:22:22:22"
              )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'themes/hotspot_index.html')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CustomerDataSaveTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', email='email@helo.com', password='testpassword')
        self.user.save()

        self.org = Organization(
            id='d773b604-2457-4b0a-b224-555555555555',
            name='Test Org',
            location='test',
            cover_image=get_temporary_image(),
            logo=get_temporary_image(),
            owner=self.user
        )
        self.org.save()

    def test_001_client_url_is_valid(self):
        self.assertEqual(reverse('wifiportal:saveCustomer'), '/portal/customer/')

    def test_invalid_data_no_organization(self):
        response = self.client.post(reverse('wifiportal:saveCustomer'), data=dict())
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['content-type'], 'application/json')

    def test_invalid_data_no_customer_data(self):
        response = self.client.post(reverse('wifiportal:saveCustomer'), data=dict(
            organization=self.org.id
        ))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['content-type'], 'application/json')

    def test_customer_name_is_required(self):
        response = self.client.post(reverse('wifiportal:saveCustomer'), data=dict(
            organization=self.org.id,
            phone_number='9857684757'
        ))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertIn('"name": ["This field is required."]', response.content)

    def test_phone_number_is_required(self):
        response = self.client.post(reverse('wifiportal:saveCustomer'), data=dict(
            organization=self.org.id,
            name='Hira Lal'
        ))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertIn('"phone_number": ["This field is required."]', response.content)

    def test_valid_customer_data(self):
        response = self.client.post(reverse('wifiportal:saveCustomer'), data=dict(
            organization=self.org.id,
            name='Pida Kumar',
            phone_number='9578457843'
        ))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertIn('"ok": true', response.content)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class RouterCredentialTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', email='email@helo.com', password='testpassword')
        self.user.save()

        self.org = Organization(
            id='d773b604-2457-4b0a-b224-555555555555',
            name='Test Org',
            location='test',
            cover_image=get_temporary_image(),
            logo=get_temporary_image(),
            owner=self.user
        )
        self.org.save()

    def test_001_url_resolution(self):
        self.assertEqual(reverse('wifiportal:getRouterCredentials'), '/portal/routerCreds/')

    def test_002_invalid_data_no_organization(self):
        response = self.client.post(reverse('wifiportal:getRouterCredentials'), data=dict())

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['content-type'], 'application/json')

    def test_003_invalid_data_no_client(self):
        response = self.client.post(reverse('wifiportal:getRouterCredentials'), data=dict(
            organization=self.org.id,
        ))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertIn('Resource Not Found', response.content)

    def test_004_invalid_data_unregistered_user(self):
        response = self.client.post(reverse('wifiportal:getRouterCredentials'), data=dict(
            organization=self.org.id,
            mac_address='21:21:12:12:23:32',
            chap_id='r',
            chap_challenge='challenge'
        ))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertIn('Resource Not Found', response.content)

    def test_005_chap_missing(self):
        self._add_customer('Ba-n-ke Lal', '21:21:12:12:23:32', '96758438492')

        response = self.client.post(reverse('wifiportal:getRouterCredentials'), data=dict(
            organization=self.org.id,
            mac_address=self.customer.mac_address,
        ))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertIn('Chapper missing', response.content)

    def test_006_everything_is_fine(self):
        self._add_customer('Ba-n-ke Lal', '21:21:12:12:23:32', '96758438492')

        response = self.client.post(reverse('wifiportal:getRouterCredentials'), data=dict(
            organization=self.org.id,
            mac_address=self.customer.mac_address,
            chap_id='r',
            chap_challenge='challenge'
        ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertIn('"username": "user1"', response.content)
        self.assertIn('"password": "58c5c21128dbd6c8dfd88420636039a6"', response.content)

    def _add_customer(self, name, mac_address, phone_number):
        self.customer = Customer.objects.get_or_create(name=name, mac_address=mac_address, phone_number=phone_number, organization=self.org)[0]
        return self.customer


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class DashboardView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', email='email@helo.com', password='testpassword')
        self.user.save()

        self.staff_user = User.objects.create_user(username='staff', email='helo@staff.com', password='staffpassword', is_staff=True)
        self.staff_user.save()

        self.staff_user_owner = User.objects.create_user(username='staff1', email='helo@staff1.com', password='staff1password', is_staff=True)

        self.super_user = User.objects.create_superuser(username='super', email='super@supter.com', password='superpassword')

        self.org = Organization(
            id='d773b604-2457-4b0a-b224-555555555555',
            name='Test Org',
            location='test',
            cover_image=get_temporary_image(),
            logo=get_temporary_image(),
            owner=self.staff_user_owner
        )
        self.org.save()

    def test_001_url_resolution(self):
        self.assertEqual(reverse('admin:dashboard'), '/login-portal/dashboard/')

    def test_002_redirect_for_not_logged_in_user(self):
        response = self.client.get(reverse('admin:dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login-portal/login/', response.url)

    def test_003_normal_user_dashboard_access(self):
        self.client.login(username='test', password='testpassword')
        response = self.client.get(reverse('admin:dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login-portal/login/', response.url)
        self.client.logout()

    def test_004_staff_user_dashboard_access(self):
        self.client.login(username=self.staff_user.username, password='staffpassword')
        response = self.client.get(reverse('admin:dashboard'))
        self.assertEqual(response.status_code, 400)
        self.client.logout()

    def test_004_001_staff_user_organization_owner_access(self):
        self.client.login(username=self.staff_user_owner.username, password='staff1password')
        response = self.client.get(reverse('admin:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_005_super_user_dashboard_access(self):
        self.client.login(username=self.super_user.username, password='superpassword')
        response = self.client.get(reverse('admin:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()
