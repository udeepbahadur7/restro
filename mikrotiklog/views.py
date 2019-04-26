# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import SuspiciousOperation
from django.http.response import HttpResponse
from django.shortcuts import render

from mikrotiklog.forms import RouterForm, RouterStatusForm
from mikrotiklog.models import Router


def router_status(request):
    mac_address = request.GET.get('mac_address', 'NA')
    nasid = request.GET.get('nasid', 'NA')

    try:
        router = Router.objects.get(mac_address=mac_address, nasid=nasid)
    except Router.DoesNotExist:
        raise SuspiciousOperation('Bad Request!! track code: z9fWHJF7')

    status_form_kwargs = request.GET.copy()
    status_form_kwargs['router'] = router.id
    status_log_form = RouterStatusForm(status_form_kwargs)
    if not status_log_form.is_valid():
        raise SuspiciousOperation('Bad request!! track-code: tZq7iBep')

    status_log_form.save()
    return HttpResponse(status=204)