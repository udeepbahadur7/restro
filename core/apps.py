from django.apps import AppConfig
from django.conf.urls import url


class DefaultAppConfig(AppConfig):
    '''
        This fix links to the 3rd party app models. This is necessary,
        because of the character of the admins 'autodiscover' function.
        Otherwise the admin site won't show the 3rd part models. Please
        followup the
        https://stackoverflow.com/questions/4877335/how-to-use-custom-adminsite-class#30056258
        '''
    name = 'core'

    def ready(self):
        from django.contrib import admin
        from django.contrib.admin import sites

        class MyAdminSite(admin.AdminSite):
            def get_urls(self):
                from dashboard.views import DashboardView

                urlpatterns = super(MyAdminSite, self).get_urls()

                return urlpatterns + [
                    url(r'^dashboard/$', self.admin_view(DashboardView.as_view()), name='dashboard'),
                ]

        mysite = MyAdminSite()
        admin.site = mysite
        sites.site = mysite