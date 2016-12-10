import json
import logging
import requests

from configuration import constant_values


class ClientConfigurationHandler:
    @staticmethod
    def get_client_configuration_from_server(configuration, client_key):
        url = "http://{0}:{1}/aps/JsonRequest".format(configuration['SERVER_IP'], configuration['SERVER_PORT'])
        headers = {"content-type": "aps/json"}
        payload = {"message": "get_client_configuration", "key": client_key}
        logger = logging.getLogger("aps")
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            logger.info("CONFIGURATION:{}".format(response.json()))
            # print("CONFIGURATION:",response.json())
            return response.json()['configuration']
        except requests.ConnectionError:
            logger = logging.getLogger("aps")
            logger.error("Could not connect to server and get configuration.")
            # print("Could not connect to server and get key.")
        return None

    @staticmethod
    def save_current_configuration(client_configuration):
        with open(constant_values.LAST_CONFIG_PATH, 'w') as file:
            json.dump(client_configuration, file)

