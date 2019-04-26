from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from mtemulator.views import login, status, hotspot_template_download

urlpatterns = [
    url(r'^login/', login, name='mtlogin'),
    url(r'^status/', status, name='mtstatus'),
    url(r'^hotspotTemplate/(?P<organization_id>([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12})/', hotspot_template_download, name='hotspotTemplate'),
]