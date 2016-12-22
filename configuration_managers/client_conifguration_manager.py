import json

from acquisition_layer.server_communicator import ServerCommunicator
from configuration import constant_values
from configuration_managers.client_key_handler import ClientKeyHandler
from utils import utils
import logging

LOGGER = logging.getLogger("aps")


class ClientConfigurationManager:
    __metaclass__ = utils.Singleton

    def __init__(self):
        self._base_configuration = self._load_initial_configuration()
        self._last_configuration = self._load_last_configuration()
        self.__server_communicator = None

    def get_client_configuration_from_server(self):
        key = ClientKeyHandler.get_assigned_client_key()
        self._last_configuration = self._server_communicator.get_client_configuration(key)
        self._save_current_configuration()
        return self._last_configuration != {}

    def __getitem__(self, item):
        try:
            return self._last_configuration[item]
        except KeyError:
            return self._base_configuration[item]

    def is_configured_by_server(self):
        return self._last_configuration != {}

    @property
    def _server_communicator(self):
        if self.__server_communicator is None:
            self.__server_communicator = ServerCommunicator(
                self
            )
        return self.__server_communicator

    def _save_current_configuration(self):
        with open(constant_values.LAST_CONFIG_PATH, 'w') as file:
            json.dump(self._last_configuration, file)

    def _load_initial_configuration(self):
        with open(constant_values.BASE_CONFIG_PATH) as configuration_file:
            return json.load(configuration_file)

    def _load_last_configuration(self):
        try:
            with open(constant_values.LAST_CONFIG_PATH) as configuration_file:
                return json.load(configuration_file)
        except IOError:
            LOGGER.info("No server configuration file detected")
            return {}
