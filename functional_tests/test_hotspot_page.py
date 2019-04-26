import tempfile

import time
from django.conf import settings
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, get_user_model, HASH_SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore
from django.test import override_settings
from django.urls import reverse

from functional_tests.base import FunctionalTest
from wifiportal.models import Organization


MEDIA_ROOT = tempfile.mkdtemp()


User = get_user_model()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class NewHotspotUser(FunctionalTest):

    def setUp(self):
        super(NewHotspotUser, self).setUp()

        # Tori Singh is a new user to the Hotspot system.
        self.user = self.create_pre_authenticated_session('superuser', 'password', 'super@duper.com')

        # He also wons a organization registerd on InfiniaSmart
        self.org = Organization(
            id='d773b604-2457-4b0a-b224-555555555555',
            name='Test Org',
            location='test',
            cover_image=self._get_temporary_image(),
            logo=self._get_temporary_image(),
            owner=self.user
        )
        self.org.save()

    def test_001_mtemulator_login_page_redirect(self):
        # Tori can access the mtemulator login url.
        self.browser.get(self.live_server_url + reverse('mtemulator:mtlogin'))
        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('wifiportal:hotspotView', kwargs=dict(organization_id=self.org.id)))

    def test_002_new_user_can_see_user_detail_form(self):
        # Tori opens his phone and connect to his wifi network. Her phone navigates to the Hotspot
        # login page.
        self.browser.get(self.live_server_url + reverse('mtemulator:mtlogin'))
        self.assertIn(self.org.name, self.browser.title)

        # She can now see customer info form.
        form_element = self.browser.find_element_by_xpath('//div[@class="partial_forms"]//form[@name="customerdata"]')
        self.assertTrue(form_element.is_displayed())

        # She sees two input field with placeholders.
        input_elements = self.browser.find_elements_by_xpath('//form[@name="customerdata"]//input')
        name_input = input_elements[0]
        contact_input = input_elements[1]

        name_placeholder = name_input.get_attribute('placeholder')
        self.assertEqual(name_placeholder, 'Your Name')

        contact_placeholder = contact_input.get_attribute('placeholder')
        self.assertEqual(contact_placeholder, 'Mobile No.')

        # Tori is curious about whether she can bypass the form and she clicks the proceed button without filling in the form
        user_info_submit_button = self.browser.find_element_by_id('id_user_info_button')
        user_info_submit_button.click()

        # Tori is prompted with error message.
        self.assertIn(
            'This field is required',
            self.browser.find_element_by_id('customer_name_error').text,
        )
        self.assertIn(
            'This field is required',
            self.browser.find_element_by_id('customer_contact_error').text,
        )

        # Tori now types in her name but she is little reluctant to give away her phonenumber.
        # So she tries random number in phone number but gets error message when tries to submit.
        name_input.send_keys("Tori Singh")
        contact_input.send_keys('85774657')
        user_info_submit_button.click()
        self.assertIn(
            "Invalid Phone Number",
            self.browser.find_element_by_id('customer_contact_error').text,)

        # Tori then clears and types her contact number. and submits the form.
        contact_input.clear()
        contact_input.send_keys("9857664657")
        user_info_submit_button.click()

        # Tori now can see Greetings and promotion page items.
        self.assertIn(
            'Hi Tori Singh',
            self.browser.find_element_by_id('id_greetings').text
        )
        # wait for animation to finish
        time.sleep(1)
        self.assertTrue(
            self.browser.find_element_by_class_name('special-items').is_displayed()
        )

        # She can see the proceed button and clicks on the proceed button.
        # Now she can see the post hotspot promo link. She can access to the internet now.

