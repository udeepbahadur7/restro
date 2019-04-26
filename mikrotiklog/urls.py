from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from mikrotiklog.views import router_status

urlpatterns = [
    url(r'^status/', router_status, name='router_status'),
]