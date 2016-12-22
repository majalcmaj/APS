import hashlib
import hmac
import json

from django.http.response import HttpResponse

from APS.settings import DIGITAL_SIGNATURE_SECRET, MESSAGE_DATA_DELIMITER
from common.libs import ClientsConfigurator


def return_client_configuration(client):
    configuration = ClientsConfigurator.form_configuration_data_for_client(client)
    ClientsConfigurator.ack_configuration_applied(client)
    return configuration


def extract_client_key(json_data):
    try:
        return int(json_data.get('key'))
    except TypeError:
        raise ValueError

class CryptUtils:
    @staticmethod
    def create_signature(data):
        return hmac.new(DIGITAL_SIGNATURE_SECRET, data, hashlib.sha256).digest()

    @staticmethod
    def validate_signature(data, signature):
        return hmac.compare_digest(
            CryptUtils.create_signature(data),
            signature
        )


def signed_json_response(data=None, status=200):
    data_json = json.dumps(data).encode("UTF-8")
    digest = CryptUtils.create_signature(data_json)
    data_json = digest + MESSAGE_DATA_DELIMITER + data_json
    return HttpResponse(status=status, content=data_json)