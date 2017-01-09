import logging
import os

from acquisition_layer import ServerCommunicator
from configuration import settings

LOGGER = logging.getLogger(settings.LOGGER_NAME)


class ClientConfigurationManager:
    def __init__(self, available_plugins):
        self._last_configuration = None
        self._available_plugins = available_plugins
        self._key = None
        try:
            if os.path.isfile(settings.CLIENT_KEY_FILE):
                with open(settings.CLIENT_KEY_FILE, 'r') as f:
                    key = int(f.readline())
                    if ServerCommunicator.validate_client_identity(key):
                        self._key = key

        except Exception:
            LOGGER.exception("An exception ocurred during acquisition of client's key.")

        if self._key is None:
            LOGGER.info("Attempting to register on a server...")
            self._key = ServerCommunicator.register_client(available_plugins)
            assert self._key is not None, "Fatal error: key cannot be none!"
            self._save_client_key()

        self.get_client_configuration_from_server()

    @property
    def key(self):
        return self._key

    @property
    def plugins_available(self):
        return self._available_plugins

    def get_client_configuration_from_server(self):
        LOGGER.info("Acquiring configuration from server.")
        self._last_configuration = ServerCommunicator.get_client_configuration(self._key)

    def __getitem__(self, item):
        return self._last_configuration[item]

    def _save_client_key(self):
        with open(settings.CLIENT_KEY_FILE, 'w') as f:
            f.write(str(self._key))