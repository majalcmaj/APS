import time
from threading import Thread, Event

from utils import utils_functions
import requests
import json


class DataSender:
    def __init__(self, command_pipe, result_pipe, server_ip, server_port, hostname):
        self.command_pipe = command_pipe
        self.result_pipe = result_pipe

        self.server_ip = server_ip
        self.server_port = server_port
        self.hostname = hostname

        self._key = None
        self._configuration = None

    def set_configuration(self, configuration):
        self._configuration = configuration

    def set_key(self, key):
        self._key = key

    def start_sending_data(self):
        parameters = " ".join(self._configuration['monitoring_parameters'])
        interval = int(self._configuration['probing_interval'])

        time.sleep(interval)
        while True:
            start_time = time.time()
            utils_functions.write_to_pipe(self.command_pipe, parameters)
            status_data = utils_functions.read_from_pipe(self.result_pipe)
            print(int(time.time()), status_data)

            url, headers, payload = self._form_status_data_request(status_data)
            try:
                response = requests.post(url, data=json.dumps(payload), headers=headers)
                print(response.json())
                if 'configuration' in response.json():
                    self._configuration = response.json()['configuration']
                    parameters = " ".join(self._configuration['monitoring_parameters'])
                    interval = int(self._configuration['probing_interval'])
                    time.sleep(interval)
                    continue

            except requests.ConnectionError:
                print("Record could not be sent")

            time_difference = time.time() - start_time
            if interval - time_difference > 0:
                time.sleep(interval - time_difference)

    def _form_status_data_request(self, status_data):
        url = "http://{}:{}/aps/JsonRequest".format(self.server_ip, self.server_port)
        headers = {"content-type": "aps/json"}
        payload = {"message": "monitoring_data",
                   "hostname": self.hostname,
                   "monitored_properties": json.loads(status_data),
                   "key": str(self._key)
                   }
        return url, headers, payload
