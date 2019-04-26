from .docker_utils import get_secret_from_docker
from .base import *

EMAIL_USE_TLS = True
EMAIL_HOST = get_secret_from_docker('EMAIL_HOST')
EMAIL_PORT = get_secret_from_docker('EMAIL_PORT')
EMAIL_HOST_USER = get_secret_from_docker('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_secret_from_docker('EMAIL_HOST_PASSWORD')

SERVER_EMAIL = 'support.infiniastores@infiniahub.com'
ADMINS = [('Sushil', 'sushil@perplexsolutions.com')]

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_secret_from_docker('POSTGRES_DB'),
        'USER': get_secret_from_docker('POSTGRES_USER'),
        'PASSWORD': get_secret_from_docker('POSTGRES_PASSWORD'),
        'HOST': 'postgres',
        'PORT': '5432',
    }
}


# Celery configurations
RABBITMQ_USER = get_secret_from_docker('RABBITMQ_DEFAULT_USER')
RABBITMQ_USER_PASSWORD = get_secret_from_docker('RABBITMQ_DEFAULT_PASS')
RABBITMQ_VHOST = get_secret_from_docker('RABBITMQ_DEFAULT_VHOST')

CELERY_BROKER_URL = "amqp://{default_user}:{default_user_password}@rabbitmq:5672/{default_vhost}".format(default_user=RABBITMQ_USER, default_user_password=RABBITMQ_USER_PASSWORD, default_vhost=RABBITMQ_VHOST)
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

CELERY_INCLUDE = ['sms.tasks']
CELERY_TASK_RESULT_EXPIRES = 60*60*24

ALLOWED_HOSTS = [get_secret_from_docker('NGINX_HOSTNAME'), 'www.'+get_secret_from_docker('NGINX_HOSTNAME')]
