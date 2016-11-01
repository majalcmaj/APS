import json
import os
import socketserver
import requests
import time
import io
import constant_values

from multiprocessing import Process
from data_sender import DataSender
from configuration_receiving_handler import ConfigurationReceiverHandler
from hardware_data_collector import HardwareDataCollector
from utils import utils_functions


class ConfigurationReceiver(socketserver.TCPServer):
    def __init__(self, command_pipe, result_pipe):
        self._load_initial_configuration()
        self.data_sender = DataSender(command_pipe, result_pipe, self._configuration['SERVER_IP'],
                                      self._configuration['SERVER_PORT'],
                                      self._configuration['HOSTNAME'])

        socketserver.TCPServer.__init__(self, ("", int(self._configuration['HOST_PORT'])), ConfigurationReceiverHandler)

    def run(self):
        if os.path.isfile(constant_values.LAST_CONFIG_PATH):
            if utils_functions.yes_no_prompt(constant_values.LAST_CONFIG_PROMPT) is True:
                configuration = self._load_last_conifguration()
                if configuration is not None:
                    self.data_sender.start_sending_data(configuration)
                    self.serve_forever()
        else:
            os.remove(constant_values.LAST_CONFIG_PATH)

        self.register_on_server(self._configuration)
        self.serve_forever()

    def _load_last_conifguration(self):
        try:
            with open(constant_values.LAST_CONFIG_PATH, 'r') as file:
                return json.load(file)
        except io.UnsupportedOperation:
            print("Could not load last configration file")
            return None

    def _load_initial_configuration(self):
        with open(constant_values.BASE_CONFIG_PATH) as configuration_file:
            self._configuration = json.load(configuration_file)

    @staticmethod
    def register_on_server(configuration):
        url = "http://{}:{}/aps/JsonRequest".format(configuration['SERVER_IP'], configuration['SERVER_PORT'])
        headers = {"content-type": "aps/json"}
        payload = {"message": "register",
                   "listening_port": configuration['HOST_PORT'],
                   "monitored_properties": configuration['MONITORED_PROPERTIES'],
                   "hostname": configuration['HOSTNAME']
                   }
        print(payload)

        while True:
            try:
                response = requests.post(url, data=json.dumps(payload), headers=headers)
                return response.status_code
            except requests.ConnectionError:
                print("Could not connect to server. Trying again...")
                time.sleep(5)


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
