import uuid

from django.contrib.auth.models import User

from functional_tests import get_temporary_image
from wifiportal.models import Organization


def create_test_org(name, location, user=None):
    if not user:
        user = User.objects.create_user(username='test', email='email@helo.com', password='testpassword')
        user.save()

    org = Organization(
        id=str(uuid.uuid4()),
        name='Test Org',
        location='test',
        cover_image=get_temporary_image(),
        logo=get_temporary_image(),
        owner=user
    )
    org.save()

    return org