import imp
import logging
import os
import re

from configuration import settings

LOGGER = logging.getLogger(settings.LOGGER_NAME)


class HardwareDataCollector:
    def __init__(self, pipe):
        self._pipe = pipe
        directory = os.listdir(settings.HARDWARE_PLUGINS_DIR)
        plugin_files = filter(lambda x: re.match("^[a-zA-Z0-9]\w*\.py$", x), directory)
        self._loaded_modules = {}
        for plugin in plugin_files:
            name = plugin.split(".")[0]
            plugin = imp.load_source(name, os.path.join(settings.HARDWARE_PLUGINS_DIR, plugin))
            if hasattr(plugin, "VALUE_UNIT") and hasattr(plugin, "read_value"):
                LOGGER.info("Loading module named '{}', which returns values of type '{}'.".format(
                    name, plugin.VALUE_UNIT))

                self._loaded_modules[name] = plugin
            else:
                raise ImportError(
                    "Module '{}' should have fields 'NAME' and 'UNIT' and function 'read_value()' declared. Aborting...")

    @property
    def available_plugins(self):
        return {name: module.VALUE_UNIT for name, module in self._loaded_modules.items()}

    def run(self):

        while True:
            input_data = self._pipe.recv()
            result = {}
            for function_name in input_data:
                result[function_name] = self._loaded_modules[function_name].read_value()
            self._pipe.send(result)
