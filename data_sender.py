import time
from threading import Thread

from utils import utils_functions
import requests
import json


class DataSender:
    def __init__(self, command_pipe, result_pipe,server_ip,server_port,hostname):
        self._is_sending_data = False
        self._sending_thread = None
        self.command_pipe = command_pipe
        self.result_pipe = result_pipe

        self.server_ip=server_ip
        self.server_port = server_port
        self.hostname = hostname

    def is_sending_data(self):
        return self._is_sending_data

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
            except requests.ConnectionError as e:
                print("Could not connect to server. Trying again...")
                time.sleep(5)

    def start_sending_data(self, configuration):
        self._is_sending_data = True
        self._sending_thread = Thread(target=self._send_status_data, kwargs={"configuration": configuration,})
        self._sending_thread.start()

    def _send_status_data(self, configuration):
        parameters = configuration['monitoring_parameters']
        interval = int(configuration['probing_interval'])

        while self._is_sending_data:
            start_time = time.time()
            utils_functions.write_to_pipe(self.command_pipe, parameters)
            result = utils_functions.read_from_pipe(self.result_pipe)
            print(result)
            url = "http://{}:{}/aps/JsonRequest".format(self.server_ip, self.server_port)
            headers = {"content-type": "aps/json"}
            payload = {"message": "monitoring_data",
                       "hostname": self.hostname,
                       "monitored_properties": json.loads(result),
                       }
            try:
                response = requests.post(url, data=json.dumps(payload), headers=headers)
                print(response)
            except Exception:
                print("record could not be sent")

            time_difference = time.time() - start_time
            if time_difference < interval:
                time.sleep(interval - time_difference)

    def stop_sending_data(self):
        self._is_sending_data = False
        if self._sending_thread is not None:
            self._sending_thread.join()
