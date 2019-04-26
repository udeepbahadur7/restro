from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from wifiportal.views import saveCustomerData, HotSpotView, validateWifiPassword, getRouterCredentials

urlpatterns = [
    #url(r'^client/(?P<client_id>([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12})/', hotspotView, name='hotspotView'),
    url(r'^client/(?P<organization_id>([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12})/', HotSpotView.as_view(), name='hotspotView'),
    url(r'^customer/', saveCustomerData, name='saveCustomer'),
    url(r'^validateHotspotPassword/', validateWifiPassword, name='validateHotspotPassword'),
    url(r'^routerCreds/', getRouterCredentials, name='getRouterCredentials'),
]