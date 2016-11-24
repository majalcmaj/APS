import requests
import json

import constant_values

class ClientConfigurationHandler:
    @staticmethod
    def get_client_configuration_from_server(configuration, client_key):
        url = "http://{0}:{1}/aps_client/JsonRequest".format(configuration['SERVER_IP'], configuration['SERVER_PORT'])
        headers = {"content-type": "aps/json"}
        payload = {"message": "get_client_configuration", "key": client_key}

        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            print("CONFIGURATION:",response.json())
            return response.json()['configuration']
        except requests.ConnectionError:
            print("Could not connect to server and get key.")
        return None

    @staticmethod
    def save_current_configuration(client_configuration):
        with open(constant_values.LAST_CONFIG_PATH, 'w') as file:
            json.dump(client_configuration, file)
