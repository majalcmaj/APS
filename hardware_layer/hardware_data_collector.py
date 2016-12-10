import json

from hardware_layer import hardware_functions
from hardware_layer.lumel_connection import LumelConnection
from utils import utils_functions


class HardwareDataCollector:
    @staticmethod
    def run(command_pipe, result_pipe, lumel_monitoring, lumel_ip, lumel_port):
        if lumel_monitoring:
            lumel_connection = LumelConnection(lumel_ip, lumel_port)
            lumel_connection.connect_with_lumel()
        else:
            lumel_connection = None

        while True:
            try:
                input_data = utils_functions.read_from_pipe(command_pipe)
                functions = HardwareDataCollector.map_parameters_onto_functions(input_data.split(" "))
                result = {}
                for function in functions:
                    if function[0].find("lumel") != -1 and lumel_monitoring:
                        result[function[0]] = function[1](lumel_connection)
                    else:
                        result[function[0]] = function[1]()
                utils_functions.write_to_pipe(result_pipe, json.dumps(result))
            except KeyboardInterrupt:
                if lumel_monitoring:
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
