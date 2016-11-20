import requests
import json
import constant_values


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
        except FileNotFoundError:
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

        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            print("KEY_VALID:", response.json())
            return response.json()['key_valid']
        except requests.ConnectionError:
            print("Could not connect to server and get key.")
        return None


