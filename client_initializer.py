import json
import os
import socketserver
from multiprocessing import Process

from data_sender import DataSender

from configuration_receiving_handler import ConfigurationReceiverHandler
from hardware_data_collector import HardwareDataCollector
from utils import utils_functions


class ConfigurationReceiver(socketserver.TCPServer):
    def __init__(self, command_pipe, result_pipe):
        self._load_initial_configuration()
        self.data_sender = DataSender(command_pipe, result_pipe)
        socketserver.TCPServer.__init__(self, ("", int(self._configuration['HOST_PORT'])), ConfigurationReceiverHandler)

    def get_sending_thread(self):
        return self.sending_thread

    def run(self):
        response = DataSender.register_on_server(self._configuration)
        if response is 200:
            self.serve_forever()

    def _load_initial_configuration(self):
        with open("configuration/base_config.json") as configuration_file:
            self._configuration = json.load(configuration_file)

    def get_server_ip(self):
        return self._server_ip

    def get_server_port(self):
        return self._server_port


if __name__ == '__main__':
    r_command_pipe, w_command_pipe = os.pipe()
    r_result_pipe, w_result_pipe = os.pipe()

    hardware_data_collector_process = Process(target=HardwareDataCollector.run, kwargs={
        "command_pipe": r_command_pipe,
        "result_pipe": w_result_pipe,
    })
    hardware_data_collector_process.start()

    utils_functions.drop_privileges('artur', 'artur')
    ConfigurationReceiver(w_command_pipe, r_result_pipe).run()
