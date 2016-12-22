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
    def is_key_valid(server_communicator, client_key):
        return server_communicator.validate_client_identity(client_key)

