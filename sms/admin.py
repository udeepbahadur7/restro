import json

from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.db.models import Count, Case, When
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from rangefilter.filter import DateRangeFilter

from dashboard.views import get_users_timezone
from sms.forms import CustomerFilter
from sms.models import SMS, CustomerSMS
from sms.tasks import send_sms
from sms.views import CustomerPreview


class SMSModelAdmin(ModelAdmin):
    actions = None
    list_display_links = None
    exclude = ('creation_timestamp',)

    def get_list_display(self, request):
        list_display = ['message', 'scheduled_timestamp', 'sms_count', 'retry_button', 'status_check_button', 'payment_received']
        if request.user.has_perm('alter_all_SMS'):
            return list_display + ['pay_button']
        return list_display

    def get_exclude(self, request, obj=None):
        timezone.activate(get_users_timezone(request.user))
        exclude = ['creation_timestamp']
        if request.user.has_perm('alter_all_SMS'):
            return exclude
        return exclude + ['organization']

    def sms_count(self, obj):
        return "{success} of {total} sms sent".format(success=obj.successful_sms, total=obj.total_sms)

    def pay_button(self, obj):
        if (obj.payment_received):
            return ''
        return format_html('<a href={pay_link} class="button" style="background:#07AB83">Pay</a>',
                           pay_link=reverse("admin:sms_sms_paymentsms", args=(obj.id,)))

    def retry_button(self, obj):
        if (obj.payment_received):
            return ''
        if (obj.successful_sms < obj.total_sms):
            return format_html(
                '<a href={retry_link} class="button" style="background:#0783AB">Retry</a>',
                retry_link=reverse("admin:sms_sms_retrysms", args=(obj.id,))
            )
        return ''
    retry_button.short_description = 'Retry'

    def status_check_button(self, obj):
        return format_html(
            '<a href={retry_link} class="button" style="background:#0783AB">Check Status</a>',
            retry_link=reverse("admin:sms_customersms_changelist") + '?sms=' + str(obj.id)
        )

    def get_queryset(self, request):
        base_query_set = super(SMSModelAdmin, self).get_queryset(request)

        query_set = base_query_set.annotate(
            successful_sms=Count(Case(When(customersms__status='SUCCESS', then=0)))
        ).annotate(
            total_sms=Count('customersms')
        )

        if request.user.has_perm('alter_all_SMS'):
            return query_set
        return query_set.filter(organization__owner=request.user)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        customer_filter = CustomerFilter(request.POST)
        extra_context = extra_context or dict()
        extra_context.update(customer_filter=customer_filter)
        return super(SMSModelAdmin, self).changeform_view(request, object_id=object_id, form_url=form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        timezone.activate(get_users_timezone(request.user))
        if not request.user.has_perm('alter_all_SMS'):
            if hasattr(request.user, 'organization'):
                obj.organization = request.user.organization

        super(SMSModelAdmin, self).save_model(request, obj, form, change)

        customer_filter = CustomerFilter(request.POST, request=request)
        customers = customer_filter.qs
        for customer in customers:
            customer_sms_entry = CustomerSMS(receiver=customer, sms=obj, sms_gateway='SPARROW_SMS')
            customer_sms_entry.save()
            self._send_sms((customer_sms_entry.id, ), eta=obj.scheduled_timestamp)

    def get_urls(self):
        urls = super(SMSModelAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name
        custom_urls = [
            url(r'^preview_customer/$', self.admin_site.admin_view(CustomerPreview.as_view()), name='%s_%s_previewlist' % info),
            url(r'^(.+)/retry_sms/$', self.admin_site.admin_view(self.retry_sms_view), name='%s_%s_retrysms' % info),
            url(r'^(.+)/sms_payment_received/$', self.admin_site.admin_view(self.sms_payment_received_view), name='%s_%s_paymentsms' % info),
        ]
        return custom_urls + urls

    def retry_sms_view(self, request, sms_id):
        sms_obj = self.get_queryset(request).get(pk=sms_id)
        customer_sms_items = CustomerSMS.objects.filter(sms=sms_id, status__in=['PENDING', 'FAILED'])
        messages.add_message(request, messages.INFO, u'SMS "{sms_obj}" has be queued for retry.'.format(sms_obj=sms_obj))
        for individual_customer in customer_sms_items:
            individual_customer.status = 'PENDING'
            individual_customer.save()
            self._send_sms((individual_customer.id,), eta=sms_obj.scheduled_timestamp)
        return redirect(reverse('admin:sms_sms_changelist'))

    def sms_payment_received_view(self, request, sms_id):
        sms_obj = self.get_queryset(request).get(pk=sms_id)
        messages.add_message(request, messages.INFO,
                             u'SMS "{sms_obj}" payment succeeded.'.format(sms_obj=sms_obj))
        sms_obj.payment_received = True
        sms_obj.save()
        return redirect(reverse('admin:sms_sms_changelist'))

    def _send_sms(self, args, eta):
        send_sms.apply_async(args, eta=eta)


class CustomerSMSModelAdmin(ModelAdmin):
    list_filter = [('sms__scheduled_timestamp', DateRangeFilter), 'status']

    def status_message(self, obj):
        status_detail = obj.status_detail
        try:
            status_detail_json = json.loads(status_detail)
            return status_detail_json.get('response', None)
        except Exception:
            return None

    def colored_status(self, obj):
        COLOR_CODE = dict(SUCCESS='#2ecc71', FAILED='#e74c3c', PENDING='#f1c40f')
        return format_html('''<div style="color:{color}">{status}</div''',
                           color=COLOR_CODE.get(obj.status, '#f1c40f'),
                           status=obj.status
                           )
    colored_status.admin_order_field = 'status'

    def get_scheduled_timestamp(self, obj):
        return obj.sms.scheduled_timestamp
    get_scheduled_timestamp.admin_order_field = 'scheduled_timestamp'
    get_scheduled_timestamp.short_description = 'Scheduled Timestamp'

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if request.user.has_perm('alter_all_CustomerSMS'):
            return super(CustomerSMSModelAdmin, self).changeform_view(request, object_id, form_url, extra_context)
        return redirect('admin:sms_customersms_changelist')

    def get_list_display(self, request):
        list_display = ['receiver', 'sms', 'get_scheduled_timestamp', 'colored_status', 'status_message']
        if request.user.has_perm('alter_all_CustomerSMS'):
            return list_display + ['status_detail']
        return list_display

    def get_queryset(self, request):
        timezone.activate(get_users_timezone(request.user))
        query_set = super(CustomerSMSModelAdmin, self).get_queryset(request)
        if request.user.has_perm('alter_all_CustomerSMS'):
            return query_set
        return query_set.filter(sms__organization__owner=request.user)


admin.site.register(SMS, SMSModelAdmin)
admin.site.register(CustomerSMS, CustomerSMSModelAdmin)
