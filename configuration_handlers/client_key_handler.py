import json
import logging
import requests

from configuration import constant_values


class ClientKeyHandler:
    @staticmethod
    def get_assigned_client_key():
        try:
            with open(constant_values.CLIENT_KEY_FILE, 'r') as file:
                try:
                    key = int(file.readline())
                    return key
                except TypeError:
                    return None
        except EnvironmentError:
            return None

    @staticmethod
    def save_client_key(key):
        with open(constant_values.CLIENT_KEY_FILE, 'w') as file:
            file.write(str(key))

    @staticmethod
    def is_key_valid(configuration,client_key):
        url = "http://{0}:{1}/aps/JsonRequest".format(configuration['SERVER_IP'], configuration['SERVER_PORT'])
        headers = {"content-type": "aps/json"}
        payload = {"message": "is_key_valid", "key": client_key}
        logger = logging.getLogger("aps")

        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            logger.info("KEY_VALID: {}".format(response.json()))
            # print("KEY_VALID:", response.json())
            return response.json()['key_valid']
        except requests.ConnectionError:
            logger.error("Could not connect to server and get key.")
            # print("Could not connect to server and get key.")
        return None


