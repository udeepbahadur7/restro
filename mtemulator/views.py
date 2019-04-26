# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.management import call_command
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve

from wifiportal.management.commands.createmtpages import MIKROTIK_PAGES_ZIP_EXPORT_PATH
from wifiportal.models import Organization


DEFAULT_HOTSPOT_PAGE_ORGANIZATION_ID = 'd773b604-2457-4b0a-b224-3ab672439a57'


@csrf_exempt
@login_required
def login(request):
    if (request.POST) :
        return redirect(request.POST['dst'])

    try:
        organization_id = request.user.organization.id
    except Organization.DoesNotExist:
        organization_id = DEFAULT_HOTSPOT_PAGE_ORGANIZATION_ID

    context = dict(
        organization_id= organization_id,

        simulated_chap_id='46',
        simulated_mac='aa:aa:aa:aa:aa:aa',
        simulated_ip='192.168.88.122',
        simulated_username='user1',
        simulated_link_orig='http://i.giphy.com/XGSqXkATD3Akw.gif',
        simulated_error='',
        simulated_chap_challenge='thisischapchallenge',
    )

    return render(request, 'mikrotik_simulator/mtlogin.html', context=context)


def status(request):
    return render(request, 'mikrotikpages/status.html')


@user_passes_test(lambda user: user.is_superuser)
def hotspot_template_download(request, organization_id):
    call_command('createmtpages', organization_id, verbosity=0)
    return serve(request,
                 os.path.basename(MIKROTIK_PAGES_ZIP_EXPORT_PATH),
                 os.path.dirname(MIKROTIK_PAGES_ZIP_EXPORT_PATH)
                 )
