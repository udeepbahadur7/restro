# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.utils import timezone
from django.utils.html import format_html

from mikrotiklog.models import Router, StatusLog


class RouterModelAdmin(ModelAdmin):
    list_display = ('nasid', 'mac_address', 'status_flag')

    def status_flag(self, obj):
        router_status_log = obj.statuslog_set.order_by('-entry_timestamp')
        if not router_status_log:
            return "NA"

        last_entry = router_status_log[0]
        delta_time = timezone.now() - last_entry.entry_timestamp

        return format_html('''<div>{delta_time}<div style="background-color:{status_color};border:#eaeaea 2px solid;border-radius:10px;width:16px;height:16px;float:left;margin: 0px 10px;"></div></div>''',
                           status_color=self.get_timedelta_color_code(delta_time),
                           delta_time=delta_time
                           )

    def get_timedelta_color_code(self, delta_time):
        if delta_time > timezone.timedelta(days=1):
            return "#e74c3c"
        elif delta_time > timezone.timedelta(hours=8):
            return "#f1c40f"
        elif delta_time > timezone.timedelta(hours=1):
            return "#3498db"
        return "#2ecc71"


class StatusLogModelAdmin(ModelAdmin):
    list_display = ('router', 'system_time', 'uptime', 'load_average', 'entry_timestamp')


admin.site.register(Router, RouterModelAdmin)
admin.site.register(StatusLog, StatusLogModelAdmin)