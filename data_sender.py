import time
from threading import Thread, Event

from utils import utils_functions
import requests
import json


class DataSender:
    def __init__(self, command_pipe, result_pipe, server_ip, server_port, hostname, base_probing_interval):
        self.command_pipe = command_pipe
        self.result_pipe = result_pipe

        self.server_ip = server_ip
        self.server_port = server_port
        self.hostname = hostname

        self._key = None
        self._configuration = None
        self._base_probing_interval = base_probing_interval

    def set_configuration(self, configuration):
        self._configuration = configuration

    def set_key(self, key):
        self._key = key

    def start_sending_data(self):
        parameters = " ".join(self._configuration['monitoring_parameters'])
        base_probing_interval = self._base_probing_interval

        counter = int(self._configuration['probing_interval'])
        aggregator = {}
        for p in parameters.split(" "):
            aggregator[p] = 0

        # agregator = {p: 0 for p in parameters.split(" ")}

        while True:
            if counter == 0:
                divider = int(self._configuration['probing_interval'])

                for k, v in aggregator.items():
                    aggregator[k] = str(round(v / divider, 2))

                # agregator = {k: str(round(v / divider, 2)) for k, v in agregator.items()}
                print("SEND:", int(time.time()), aggregator)

                # sending data
                url, headers, payload = self._form_status_data_request(aggregator)
                try:
                    response = requests.post(url, data=json.dumps(payload), headers=headers)
                    print(response.json())
                    if 'configuration' in response.json():
                        self._configuration = response.json()['configuration']
                        parameters = " ".join(self._configuration['monitoring_parameters'])
                        counter = int(self._configuration['probing_interval'])
                        # agregator = {p: 0 for p in parameters.split(" ")}
                        for p in parameters.split(" "):
                            aggregator[p] = 0

                except requests.ConnectionError:
                    print("Record could not be sent")

                counter = int(self._configuration['probing_interval'])
                # aggregator = {p: 0 for p in parameters.split(" ")}
                for p in parameters.split(" "):
                    aggregator[p] = 0
            else:
                start_time = time.time()
                utils_functions.write_to_pipe(self.command_pipe, parameters)
                status_data = utils_functions.read_from_pipe(self.result_pipe)
                status_data = json.loads(status_data)
                for k, v in status_data.items():
                    aggregator[k] += float(v)

                print(status_data)

                counter -= 1
                time_difference = time.time() - start_time
                if base_probing_interval - time_difference > 0:
                    time.sleep(base_probing_interval - time_difference)

    def _form_status_data_request(self, agregator):
        url = "http://{0}:{1}/aps/JsonRequest".format(self.server_ip, self.server_port)
        headers = {"content-type": "aps/json"}
        payload = {"message": "monitoring_data",
                   "hostname": self.hostname,
                   "monitored_properties": agregator,
                   "key": str(self._key),
                   "timestamp": int(time.time())
                   }
        return url, headers, payload
