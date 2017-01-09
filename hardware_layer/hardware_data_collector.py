import json
import logging

from configuration import settings
from hardware_layer import hardware_functions
from hardware_layer.lumel_connection import LumelConnection
from utils import utils

LOGGER = logging.getLogger(settings.LOGGER_NAME)


class HardwareDataCollector:
    @staticmethod
    def run(command_pipe, result_pipe):
        if settings.LUMEL_MONITORING:
            lumel_connection = LumelConnection(settings.LUMEL_IP, settings.LUMEL_PORT)
            lumel_connection.connect_with_lumel()
        else:
            lumel_connection = None

        while True:
            try:
                input_data = utils.read_from_pipe(command_pipe)
                functions = HardwareDataCollector.map_parameters_onto_functions(input_data)
                result = {}
                for function in functions:
                    if settings.LUMEL_MONITORING and function[0].find("lumel") != -1:
                        result[function[0]] = function[1](lumel_connection)
                    else:
                        result[function[0]] = function[1]()
                utils.write_to_pipe(result_pipe, result)
            except KeyboardInterrupt:
                LOGGER.exception("An exception has ocurred during hardware data collecting.")
                if settings.LUMEL_MONITORING:
                    lumel_connection.close_connection()
                break

    @staticmethod
    def map_parameters_onto_functions(parameters):
        functions = []
        for parameter in parameters:
            try:
                functions.append((parameter, getattr(hardware_functions, 'get_' + parameter)))
            except AttributeError:
                functions.append((parameter, hardware_functions.get_not_found_parameter))

        return functions
