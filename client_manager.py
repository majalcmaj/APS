import json
import os
import socket
import time
from multiprocessing import Process

import requests

import constant_values
import utils.utils_functions as utils_functions
from configuration_handlers.client_conifguration_handler import ClientConfigurationHandler
from configuration_handlers.client_key_handler import ClientKeyHandler
from data_sender import DataSender
from hardware_data_collector import HardwareDataCollector
from interrupt_handler import InterruptHandler


class ClientManager:
    def __init__(self, command_pipe, result_pipe, configuration):
        self._configuration = configuration
        self._client_key = None
        self._current_data_configuration = None
        self._data_sender = DataSender(command_pipe, result_pipe, self._configuration['SERVER_IP'],
                                       self._configuration['SERVER_PORT'],

                                       int(self._configuration['BASE_PROBING_INTERVAL']))

    def run(self):
        interrupt_handler = InterruptHandler()
        interrupt_handler.register_interrupt_handler()

        # if we already have key then we dont have to register on server
        self._client_key = ClientKeyHandler.get_assigned_client_key()
        print("CURRENT KEY:", self._client_key)

        if self._client_key is None or ClientKeyHandler.is_key_valid(self._configuration,self._client_key) is False:
            # getting authorization key for next steps
            response = self.register_on_server(self._configuration)
            if response.status_code == 200:
                self._client_key = response.json()['key']
                ClientKeyHandler.save_client_key(self._client_key)
            elif response.status_code == 403:
                print("Could not connect to server during registration:", response.status_code)
                exit(-1)

        # getting configuration from server
        self.get_configuration()

        # start sending data
        if self._current_data_configuration is not None:
            self._data_sender.set_configuration(self._current_data_configuration)
            self._data_sender.set_key(self._client_key)
            self._data_sender.start_sending_data()

    def register_on_server(self, configuration):
        url = "http://{0}:{1}/aps_client/JsonRequest".format(configuration['SERVER_IP'], configuration['SERVER_PORT'])
        headers = {"content-type": "aps/json"}
        payload = {"message": "register",
                   "monitored_properties": configuration['MONITORED_PROPERTIES'],
                   "hostname": socket.gethostname(),
                   "base_probing_interval": configuration['BASE_PROBING_INTERVAL']
                   }

        while True:
            try:
                response = requests.post(url, data=json.dumps(payload), headers=headers)
                print("Connected to server")
                return response
            except requests.ConnectionError:
                print("Could not connect to server. Trying again...")
                time.sleep(5)

    def get_configuration(self):
        while True:
            client_configuration = ClientConfigurationHandler.get_client_configuration_from_server(self._configuration,
                                                                                                   self._client_key)
            if client_configuration is not None:
                self._current_data_configuration = client_configuration
                ClientConfigurationHandler.save_current_configuration(client_configuration)
                break
            else:
                print("Configuration is not set by server")

            time.sleep(5)


def load_initial_configuration():
    with open(constant_values.BASE_CONFIG_PATH) as configuration_file:
        return json.load(configuration_file)


if __name__ == '__main__':
    configuration = load_initial_configuration()

    r_command_pipe, w_command_pipe = os.pipe()
    r_result_pipe, w_result_pipe = os.pipe()
    hardware_data_collector_process = Process(target=HardwareDataCollector.run, kwargs={
        "command_pipe": r_command_pipe,
        "result_pipe": w_result_pipe,
        "lumel_monitoring": configuration['LUMEL_MONITORING'],
        "lumel_ip": configuration['LUMEL_IP'],
        "lumel_port": configuration['LUMEL_PORT'],
    })

    hardware_data_collector_process.start()
    utils_functions.drop_privileges(configuration['BASE_USERNAME'], configuration['BASE_USER_GROUP'])

    ClientManager(w_command_pipe, r_result_pipe, configuration).run()
