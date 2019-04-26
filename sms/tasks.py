from __future__ import absolute_import, unicode_literals

from celery.utils.log import get_task_logger
from requests import Timeout, ConnectTimeout, HTTPError, ConnectionError, RequestException

from restrocloud.celery import celery_app as app
from sms.models import CustomerSMS
from sms.sms_gateway.sparrow_sms_gateway import SparrowSMSGateway


logger = get_task_logger(__name__)


task_autoretry_kwargs = dict(
    auto_retry_for_exceptions=(ConnectionError, HTTPError, Timeout, ConnectTimeout),
    retry_kwargs={'max_retries': 5},
    default_retry_delay=10
)


@app.task(ignore_result=True, rate_limit='600/m', time_limit=60*10, **task_autoretry_kwargs)
def send_sms(customer_sms_id):
    try:
        message_to_send = CustomerSMS.objects.get(pk=customer_sms_id)
    except CustomerSMS.DoesNotExist:
        pass

    if message_already_sent(message_to_send):
        logger.info('sms already sent !!!')
        return

    if message_to_send.sms_gateway == 'SPARROW_SMS':
        SparrowSMSGateway(message_to_send).send()
    else:
        message_to_send.status = 'FAILED'
        message_to_send.status_detail = "Invalid SMS Gateway!!! " + message_to_send.sms_gateway
        message_to_send.save()


def message_already_sent(customer_sms_obj):
    return customer_sms_obj.status == 'SUCCESS'