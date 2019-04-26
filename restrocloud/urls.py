"""restrocloud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from wifiportal.views import indexView

urlpatterns = [
    url(r'^$', indexView),
    url(r'^login-portal/', admin.site.urls),
    url(r'^portal/', include('wifiportal.urls', namespace='wifiportal')),
    url(r'^mtemulator/', include('mtemulator.urls', namespace='mtemulator')),
    url(r'^routerlog/', include('mikrotiklog.urls', namespace='mikrotiklog')),

    url(r'^docs/', include('docs.urls', namespace='infiniadocs')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
