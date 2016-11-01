import json

import hardware_functions
from utils import utils_functions


class HardwareDataCollector:
    @staticmethod
    def run(command_pipe, result_pipe):
        while True:
            try:
                input_data = utils_functions.read_from_pipe(command_pipe)
                functions = HardwareDataCollector.map_parameters_onto_functions(input_data.split(" "))
                result = {}
                for function in functions:
                    result[function[0]] = function[1]()
                utils_functions.write_to_pipe(result_pipe, json.dumps(result))
            except KeyboardInterrupt:
                break

    @staticmethod
    def map_parameters_onto_functions(parameters):
        functions = []
        for parameter in parameters:
            try:
                functions.append((parameter, getattr(hardware_functions, 'get_' + parameter)))
            except AttributeError:
                functions.append((parameter,hardware_functions.get_not_found_parameter))

        return functions