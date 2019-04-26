# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import shutil
import tempfile

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase, override_settings

# Create your tests here.
from django.urls import reverse
from io import BytesIO

from functional_tests import get_temporary_image
from mtemulator.views import DEFAULT_HOTSPOT_PAGE_ORGANIZATION_ID
from wifiportal.models import Organization


class MikrotikHotspotLoginSimulatorAnonymousUser(TestCase):

    def test_001_hotspot_emulator_url(self):
        self.assertEqual(reverse('mtemulator:mtlogin'), '/mtemulator/login/')

    def test_002_hotspot_page_anonymous_user_access(self):
        response = self.client.get(reverse('mtemulator:mtlogin'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/mtemulator/login/')


MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class MikrotikHotspotLoginSimulatorRestaurantOwner(TestCase):

    def setUp(self):
        user = User.objects.create_user(username='testuser', password='testpassword', email='test@test.com')
        user.save()

        org = Organization(
            id='d773b604-2457-4b0a-b224-555555555555',
            name='Test Org',
            location='test',
            cover_image=get_temporary_image(),
            logo=get_temporary_image(),
            owner=user
        )
        org.save()

        self.client.login(username='testuser', password='testpassword')

    def tearDown(self):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def test_001_hotspot_emulator_status_code(self):
        response = self.client.get(reverse('mtemulator:mtlogin'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('mikrotik_simulator/mtlogin.html')
        self.assertEqual(str(response.context['organization_id']), 'd773b604-2457-4b0a-b224-555555555555')


class MikrotikHotspotLoginSimulatorNoOwnerUser(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser', password='testpassword', email='test@test.com')
        user.save()

        self.client.login(username='testuser', password='testpassword')

    def test_001_hotspot_emulator_has_default_organization_id_page(self):
        response = self.client.get(reverse('mtemulator:mtlogin'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['organization_id']), DEFAULT_HOTSPOT_PAGE_ORGANIZATION_ID)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class HotSpotTemplateGeneratorTest(TestCase):
    def setUp(self):
        user = User.objects.create_superuser(username='superuser', password='superpassword', email='test@test.com')
        normal_user = User.objects.create_user(username='normaluser', password='normalpassword', email='test@test.com')

        self.org = Organization(
            id='d773b604-2457-4b0a-b224-555555555555',
            name='Test Org',
            location='test',
            cover_image=get_temporary_image(),
            logo=get_temporary_image(),
            owner=user
        )
        self.org.save()

    def tearDown(self):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def test_001_anonymous_user_cant_access_url(self):
        response = self.client.get(reverse("mtemulator:hotspotTemplate", kwargs=dict(organization_id=self.org.id)))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login', response.url)

    def test_002_normal_user_cant_access_url(self):
        self.client.login(username='normaluser', password='normalpassword')

        response = self.client.get(reverse("mtemulator:hotspotTemplate", kwargs=dict(organization_id=self.org.id)))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login', response.url)

        self.client.logout()

    def test_003_only_super_user_can_access_url(self):
        self.client.login(username='superuser', password='superpassword')

        response = self.client.get(reverse("mtemulator:hotspotTemplate", kwargs=dict(organization_id=self.org.id)))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response['content-type'], 'application/zip')

        self.client.logout()
