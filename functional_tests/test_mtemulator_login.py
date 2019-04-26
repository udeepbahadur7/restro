import tempfile

from django.test import override_settings
from django.urls import reverse

from functional_tests.base import FunctionalTest
from wifiportal.models import Organization

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class MtSimulatorAnonymousUser(FunctionalTest):

    def setUp(self):
        super(MtSimulatorAnonymousUser, self).setUp()

    def tearDown(self):
        super(MtSimulatorAnonymousUser, self).tearDown()

    def test_001_test_user_redirect(self):
        # Mai Ke Lal has not logged in to the system. He knows the
        # hotspot simulator url. He tries to access the hotspot page.
        self.browser.get(self.live_server_url + reverse('mtemulator:mtlogin'))

        # He gets redirected to login page. Good luck with that Mai Ke Lal
        self.assertEqual(self.browser.current_url, self.live_server_url+'/accounts/login/?next=/mtemulator/login/')


class MtSimulatorOrganizationOwner(FunctionalTest):
    
    def setUp(self):
        super(MtSimulatorOrganizationOwner, self).setUp()
        # Ghanshyam has InfiniaSmart in his restaurant. He has access
        # to the admin portal of Infiniasmart. He navigates to the site
        # and login using his credentials.
        self.user = self.create_pre_authenticated_session('testuser', 'password', 'test@test.com')
        self.org = Organization(
            id='d773b604-2457-4b0a-b224-555555555555',
            name='Test Org',
            location='test',
            cover_image=self._get_temporary_image(),
            logo=self._get_temporary_image(),
            owner=self.user
        )
        self.org.save()

    def tearDown(self):
        super(MtSimulatorOrganizationOwner, self).tearDown()

    def test_001_user_can_access_hotspot_page(self):
        # Ghanshyam can access the mtlogin simulator page.
        self.browser.get(self.live_server_url + reverse('mtemulator:mtlogin'))

        # He can now see the hotspot page of his restaurant.
        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('wifiportal:hotspotView', kwargs=dict(organization_id='d773b604-2457-4b0a-b224-555555555555')))
        self.assertIn('Test Org', self.browser.title)