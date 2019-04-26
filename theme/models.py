# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import uuid

from django.db import models
from django.conf import settings

def get_available_templates():
    theme_template_folder = os.path.join(settings.BASE_DIR, 'theme/templates/themes')
    return (
        (os.path.join("themes/", filepath), os.path.join("themes/", filepath))
        for filepath in os.listdir(theme_template_folder)
        if os.path.isfile(os.path.join(theme_template_folder, filepath))
    )


class PortalTheme(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template_path = models.CharField('Path to the template', max_length=100, choices=get_available_templates())
    price = models.IntegerField('Price for the template')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

