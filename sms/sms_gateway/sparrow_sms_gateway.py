import requests
from restrocloud.settings.docker_utils import get_secret_from_docker
from sms.sms_gateway.sms_gateway_base import SMSGatewayBase


SPARROW_API_KEY = get_secret_from_docker('SPARROW_API_KEY')


class SparrowSMSGateway(SMSGatewayBase):
    def _send_sms(self, message, phone_number):
        response = requests.get(
            'http://api.sparrowsms.com/v2/sms/',
            timeout=(self.connect_timeout, self.read_timeout),
            params={
                'from': 'Demo',
                'text': message,
                'to': phone_number,
                'token': SPARROW_API_KEY
            }
        )
        if response.status_code == 200:
            self.report_success(response.text)
        else:
            self.report_error(response.text)


