from __future__ import absolute_import, unicode_literals

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restrocloud.settings.production')


celery_app = Celery(main='restrocloud')

celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()

if __name__ == '__main__':
    celery_app.start()
