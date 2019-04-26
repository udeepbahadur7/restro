# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from actstream import action
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation, ValidationError, PermissionDenied
from django.http.response import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from wifiportal.forms import MikrotikForm, CustomerForm
from wifiportal.models import Commodity, Organization, Customer, HotspotConfig


def indexView(request):
    return render(request, template_name='index.html')


@method_decorator(csrf_exempt, name='dispatch')
class HotSpotView(TemplateView):
    template_name = 'themes/hotspot_index.html'

    def get(self, request, *args, **kwargs):
        return HttpResponseBadRequest("Bad Request")

    def post(self, *args, **kwargs):
        return super(HotSpotView, self).get(*args, **kwargs)

    def get_validated_mikrotik_form(self):
        mikrotikForm = MikrotikForm(self.request.POST)
        if not mikrotikForm.is_valid():
            raise SuspiciousOperation("Bad request")
        return mikrotikForm

    def get_context_data(self, **kwargs):
        context = super(HotSpotView, self).get_context_data(**kwargs)

        try:
            organization_id = self.kwargs.get('organization_id', '')
            organization = Organization.objects.get(pk=organization_id)
            context['organization'] = organization
        except ObjectDoesNotExist:
            raise Http404('Resource not found!!!')

        mikrotik_form = self.get_validated_mikrotik_form()
        customer=Customer.objects.get_customer(mikrotik_form.data['mac'], organization_id)
        featured_items = Commodity.objects.get_featured_items(organization_id)
        context['menu_items'] = featured_items
        context['username'] = 'user1'
        context['password'] = 'user1'
        context['mikrotik_input'] = mikrotik_form.data

        hotspot_config, created = HotspotConfig.objects.get_or_create(organization=organization)
        context['hotspot_config'] = hotspot_config

        context['can_add_advertisement_image'] = organization.owner.has_perm('wifiportal.can_add_advertisement_image')
        context['advertisement_image'] = hotspot_config.advertisement_image

        context['redirect_url_after_login'] = hotspot_config.login_redirect_page or mikrotik_form.data.get('link_orig', '')
        context['customer'] = customer

        context['new_customer'] = not context['customer']
        context['ask_hotspot_password'] = should_ask_for_password(hotspot_config, context['customer'])

        return context


def saveCustomerData(request):
    organization_id = request.POST.get('organization', '')
    mac_address = request.POST.get('mac_address', '')

    try:
        organization = Organization.objects.get(pk=organization_id)
    except (ObjectDoesNotExist, ValidationError, ValueError) as exception:
        return JsonResponse({'ok': False, 'errors': {'message': 'Resource Not Found'}}, status=404)

    customer = Customer.objects.get_customer(mac_address, organization_id)

    if not customer:
        form_context = request.POST.copy()
        form_context['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        customerForm = CustomerForm(form_context)

        if not customerForm.is_valid():
            return JsonResponse({'ok': False, 'errors': customerForm.errors}, status=400)

        customer = customerForm.save()

    return JsonResponse({'ok': True})


def should_ask_for_password(hotspot_config, customer):
    if not hotspot_config.enable_password:
        return False
    if not customer or not customer.last_login_timestamp:
        return True

    password_has_changed_since_lastlogin = hotspot_config.password_changed_timestamp > customer.last_login_timestamp
    return password_has_changed_since_lastlogin


def validateWifiPassword(request):
    organization_id = request.POST.get('organization', '')
    mac_address = request.POST.get('mac_address', '')
    hotspot_password = request.POST.get('hotspot_password', '')

    try:
        organization = Organization.objects.get(pk=organization_id)
        hotspot_config, created = HotspotConfig.objects.get_or_create(organization=organization)
    except (ObjectDoesNotExist, ValidationError, ValueError) as exception:
        return JsonResponse({'ok': False, 'errors': {'message': 'Resource Not Found!!'}}, status=404)

    customer = Customer.objects.get_customer(mac_address, organization_id)
    if not customer:
        return JsonResponse({'ok': False, 'errors': {'message': 'Resource Not Found!!'}}, status=400)

    if should_ask_for_password(hotspot_config, customer):
        if not hotspot_config.is_hotspot_password_valid(hotspot_password):
            return JsonResponse({'ok': False, 'errors': {'password_error': 'Invalid Credentials'}}, status=400)

    customer.last_login_timestamp = datetime.datetime.now()
    customer.save()

    return JsonResponse({'ok': True})


def getRouterCredentials(request):
    organization_id = request.POST.get('organization', '')
    mac_address = request.POST.get('mac_address', '')
    chap_id = request.POST.get('chap_id', None)
    chap_challenge = request.POST.get('chap_challenge', None)

    try:
        organization = Organization.objects.get(pk=organization_id)
        hotspot_config, created = HotspotConfig.objects.get_or_create(organization=organization)
    except (ObjectDoesNotExist, ValidationError, ValueError) as exception:
        return JsonResponse({'ok': False, 'errors': {'message': 'Resource Not Found!!'}}, status=404)

    customer = Customer.objects.get_customer(mac_address, organization_id)
    if not customer:
        return JsonResponse({'ok': False, 'errors': {'message': 'Resource Not Found!!'}}, status=400)

    if customer.blocked is True:
        return "errors"

    if should_ask_for_password(hotspot_config, customer):
        return JsonResponse({'ok': False, 'errors': {'message': 'You should login first !!'}}, status=400)

    username = hotspot_config.hotspot_user
    password = hotspot_config.hotspot_user_password

    if not (chap_id and chap_challenge):
        return JsonResponse({'ok': False, 'errors': {'message': 'Chapper missing !!!'}}, status=400)

    import hashlib
    super_secret = chap_id + password + chap_challenge
    super_secret = str(bytearray(map(ord, super_secret)))
    md5_password = hashlib.md5(super_secret).hexdigest()

    action.send(customer, verb="logged in", target=organization, public=True)
    return JsonResponse({'ok': True, 'username': username, 'password': md5_password})
