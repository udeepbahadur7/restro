# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import xlsxwriter

from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.core.exceptions import PermissionDenied
from django.http.response import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from rangefilter.filter import DateRangeFilter
from django.utils import timezone

from actstream.models import actor_stream

from wifiportal.models import Organization, Commodity, Customer, HotspotConfig
from dashboard.views import get_users_timezone


class CommodityModelAdmin(ModelAdmin):
    list_filter = ('featured',)

    def save_model(self, request, obj, form, change):
        if not request.user.has_perm('alter_all_menu_items'):
            if hasattr(request.user, 'organization'):
                obj.organization = request.user.organization
        return super(CommodityModelAdmin, self).save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ()
        if not request.user.has_perm('alter_all_menu_items'):
            self.exclude = ('organization',)
        return super(CommodityModelAdmin, self).get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        query_set = super(CommodityModelAdmin, self).get_queryset(request)
        if request.user.has_perm('alter_all_menu_items'):
            return query_set
        return query_set.filter(organization__owner=request.user)

    def get_list_display(self, request):
        if request.user.has_perm('alter_all_menu_items'):
            return ('name', 'description', 'organization', 'featured', 'rank')
        return ('name', 'description', 'featured', 'rank')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        try:
            extra_context['client_id'] = request.user.organization.id
        except:
            pass
        return super(CommodityModelAdmin, self).changelist_view(request, extra_context=extra_context)


class CustomerModelAdmin(ModelAdmin):
    readonly_fields = ['number_of_logins', ]
    list_display = ('blocked',)

    def number_of_logins(self, obj):
        return actor_stream(Customer.objects.get(pk=obj.id)).count()
    search_fields = ('name', 'phone_number')
    date_hierarchy = 'entry_timestamp'

    def get_actions(self, request):
        if request.user.is_superuser:
            return super(CustomerModelAdmin, self).get_actions(request)
        return None

    def save_model(self, request, obj, form, change):
        if not request.user.has_perm('alter_all_customer_data'):
            if hasattr(request.user, 'organization'):
                obj.organization = request.user.organization
        return super(CustomerModelAdmin, self).save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ()
        if not request.user.has_perm('alter_all_customer_data'):
            self.exclude = ('organization',)
        return super(CustomerModelAdmin, self).get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        timezone.activate(get_users_timezone(request.user))
        query_set = super(CustomerModelAdmin, self).get_queryset(request)
        if request.user.has_perm('alter_all_customer_data'):
            return query_set
        return query_set.filter(organization__owner=request.user)

    def get_list_display(self, request):
        if request.user.has_perm('alter_all_customer_data'):
            return ('name', 'phone_number', 'dob', 'organization', 'entry_timestamp', 'mac_address', 'user_agent', 'blocked',)
        return ('name', 'phone_number', 'dob', 'entry_timestamp', 'blocked',)

    def get_list_filter(self, request):
        if request.user.has_perm('alter_all_customer_data'):
            return (('entry_timestamp', DateRangeFilter), 'organization',)
        return (('entry_timestamp', DateRangeFilter),)

    def get_urls(self):
        urls = super(CustomerModelAdmin, self).get_urls()
        my_urls = [
            url(r'^downloadxlsx/$', self.admin_site.admin_view(self.downloadXlsx), name='downloadCustomerXlsx')
        ]
        return my_urls + urls

    def downloadXlsx(self, request):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True, 'remove_timezone': True, 'default_date_format': 'dd/mm/yyyy'})
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, 'Customer Name')
        worksheet.write(0, 1, 'Phone Number')
        worksheet.write(0, 2, 'Customer Entry Date')
        row = 1

        if not hasattr(request.user, 'organization'):
            return HttpResponseBadRequest("Bad Response")

        for customer in Customer.objects.filter(organization__id=request.user.organization.id):
            worksheet.write(row, 0, customer.name)
            worksheet.write(row, 1, customer.phone_number)
            worksheet.write_datetime(row, 2, customer.entry_timestamp)
            row += 1
        workbook.close()
        output.seek(0)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="users.xlsx"'
        response.write(output.read())
        return response


class OrganizationModelAdmin(ModelAdmin):
    def get_list_display(self, request):
        if request.user.is_superuser:
            return ('name', 'location', 'owner', 'hotspot_template')
        return ('name', 'location', 'owner')

    def hotspot_template(self, obj):
        return format_html('<a href="{}">Template</a>', reverse('mtemulator:hotspotTemplate', kwargs=dict(organization_id=obj.id)))


class HotspotConfigModelAdmin(ModelAdmin):
    def has_add_permission(cls, request):
        ''' remove add and save and add another button '''
        return False

    def is_a_wifi_password_change_request(self, request):
        return request.resolver_match.view_name == 'admin:wifi_password_change'

    def is_advertisement_image_add_request(self, request):
        return request.resolver_match.view_name == 'admin:add_advertisement_image'

    def has_wifi_password_change_permission(self, request):
        return request.user.has_perm('wifiportal.manage_hotspot_password')

    def has_advertisement_image_add_permission(self, request):
        return request.user.has_perm('wifiportal.can_add_advertisement_image')

    def save_model(self, request, obj, form, change):
        if not request.user.has_perm('wifiportal.alter_all_hotspot_config'):
            if hasattr(request.user, 'organization'):
                obj.organization = request.user.organization

        if self.is_a_wifi_password_change_request(request):
            if not self.has_wifi_password_change_permission(request):
                raise PermissionDenied
            obj.password_changed_timestamp = timezone.now()

        return super(HotspotConfigModelAdmin, self).save_model(request, obj, form, change)

    def all_except(self, exception_fields, all_fields):
        return [field for field in all_fields if field not in exception_fields]

    def get_exclude(self, request, obj=None):
        if request.user.has_perm('alter_all_hotspot_config'):
            return ('password_changed_timestamp', )
        total_fields = ('enable_advertisement_image', 'advertisement_image', 'enable_password', 'password', 'password_changed_timestamp', 'login_redirect_page', 'organization', 'hotspot_user', 'hotspot_user_password')

        if self.is_a_wifi_password_change_request(request):
            if not self.has_wifi_password_change_permission(request):
                raise PermissionDenied
            return self.all_except(['enable_password', 'password'], total_fields)

        if self.is_advertisement_image_add_request(request):
            if request.user.has_perm("wifiportal.can_add_advertisement_image"):
                return self.all_except(['advertisement_image'], total_fields)

        return self.all_except(['login_redirect_page'], total_fields)
    
    def get_queryset(self, request):
        query_set = super(HotspotConfigModelAdmin, self).get_queryset(request)
        if request.user.has_perm('alter_all_hotspot_config'):
            return query_set
        return query_set.filter(organization__owner=request.user)

    def get_list_display(self, request):
        timezone.activate(get_users_timezone(request.user))
        if request.user.has_perm('alter_all_hotspot_config'):
            return ('organization', 'enable_password', 'password_changed_timestamp' )
        return super(HotspotConfigModelAdmin, self).get_list_display(request)

    def changelist_view(self, request, extra_context=None):
        if request.user.has_perm('alter_all_hotspot_config'):
            return super(HotspotConfigModelAdmin, self).changelist_view(request, extra_context)
        try:
            organization = request.user.organization
        except:
            raise Http404('Organization Not Found!!')
        hotspot_config, created = HotspotConfig.objects.get_or_create(organization=organization)

        return redirect('admin:wifiportal_hotspotconfig_change', hotspot_config.id)
    #redirect('admin:{}_{}_change'%(obj._meta.app_label, obj._meta.model_name), args=(obj.pk,)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return self.changeform_view(request, object_id, form_url, extra_context={'show_save':False})

    def get_urls(self):
        urls = super(HotspotConfigModelAdmin, self).get_urls()
        my_urls = [
            url(r'^(.+)/change_wifi_password/$', self.admin_site.admin_view(self.change_view), name='wifi_password_change'),
            url(r'^(.+)/change_wifi_redirect/$', self.admin_site.admin_view(self.change_view), name='wifi_redirect_change'),
            url(r'^(.+)/add_advertisement_image/$', self.admin_site.admin_view(self.change_view), name='add_advertisement_image'),
        ]
        return my_urls + urls


admin.site.register(Organization, OrganizationModelAdmin)
admin.site.register(Commodity, CommodityModelAdmin)
admin.site.register(Customer, CustomerModelAdmin)
admin.site.register(HotspotConfig, HotspotConfigModelAdmin)
