import time
from PIL import Image
from django.conf import settings
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test.testcases import LiveServerTestCase
from io import BytesIO
from selenium import webdriver
import unittest

from selenium.common.exceptions import WebDriverException

MAX_WAIT = 10


class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def wait_for(self, fn):
        start_time = time.time()

        while True:
            try:
                return fn()
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                    time.sleep(0.5)

    def _get_temporary_image(self):
        io = BytesIO()
        size = (200, 200)
        color = (255, 0, 0, 0)
        image = Image.new("RGB", size, color)
        image.save(io, format='JPEG')
        image_file = InMemoryUploadedFile(io, None, 'foo.jpg', 'jpeg',
                                          image.size, None)
        image_file.seek(0)
        return image_file

    def create_pre_authenticated_session(self, username, password, email, superuser=False):
        if superuser:
            user = User.objects.create_superuser(username=username, password=password, email=email)
        else:
            user = User.objects.create(email=email)

        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session[HASH_SESSION_KEY] = user.get_session_auth_hash()
        session.save()

        ## to set a cookie we need to first visit the domain.
        ## 404 pages load the quickest!
        self.browser.get(self.live_server_url + "/404_no_such_url/")
        self.browser.add_cookie(dict(
            name = settings.SESSION_COOKIE_NAME,
            value = session.session_key,
            path = '/'
        ))
        self.browser.refresh()

        return user


class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_get_to_site(self):
        self.browser.get(self.live_server_url)
        self.assertIn('Infinia Smart', self.browser.title)


class RouterStatusLogTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()
