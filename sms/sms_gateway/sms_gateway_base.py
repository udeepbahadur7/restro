import requests
from requests import Timeout, ConnectTimeout, HTTPError, ConnectionError, RequestException


class SMSFailed(Exception):
    def __init__(self, message):
        self.message = message
        super(SMSFailed, self).__init__(message)


class SMSGatewayBase(object):
    connect_timeout, read_timeout = 5.0, 30.0

    def __init__(self, customer_sms_obj):
        self.customer_sms_obj = customer_sms_obj
        super(SMSGatewayBase, self).__init__()

    def _send_sms(self, message, phone_number):
        '''
        Sends requests to gateway and
        Raises SMSFailed if sms send fails

        :param message:
        :param phone_number:
        :return:
        '''
        raise NotImplementedError

    def report_error(self, status_message):
        self.customer_sms_obj.status = 'FAILED'
        self.customer_sms_obj.status_detail = status_message
        self.customer_sms_obj.save()

    def report_success(self, status_message):
        self.customer_sms_obj.status = 'SUCCESS'
        self.customer_sms_obj.status_detail = status_message
        self.customer_sms_obj.save()

    def send(self):
        message = self.customer_sms_obj.sms.message
        phone_number = self.customer_sms_obj.receiver.phone_number

        try:
            self._send_sms(message, phone_number)
        except (ConnectionError, HTTPError) as e:
            self.report_error('Request Connection Failed !!')
            raise e
        except (Timeout, ConnectTimeout) as e:
            self.report_error('Request Timeout Failed !!')
            raise e
        except RequestException as e:
            self.report_error('Request Failed !!')
        except SMSFailed as e:
            self.report_error(e.message)