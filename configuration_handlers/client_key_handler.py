import requests
import json
import constant_values


class ClientKeyHandler:
    @staticmethod
    def get_assigned_client_key():
        with open(constant_values.CLIENT_KEY_FILE, 'r') as file:
            try:
                key = int(file.readline())
                return key
            except TypeError:
                return None

    @staticmethod
    def save_client_key(key):
        with open(constant_values.CLIENT_KEY_FILE, 'w') as file:
            file.write(str(key))


