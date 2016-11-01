import time
from threading import Thread, Event

from utils import utils_functions
import requests
import json


class DataSender:
    def __init__(self, command_pipe, result_pipe, server_ip, server_port, hostname):
        self._sending_thread = None
        self._interrupt_event = None
        self.command_pipe = command_pipe
        self.result_pipe = result_pipe

        self.server_ip = server_ip
        self.server_port = server_port
        self.hostname = hostname

    def start_sending_data(self, configuration):
        self._interrupt_event = Event()
        self._sending_thread = Thread(target=self._send_status_data, kwargs={"configuration": configuration,
                                                                             "interrupt_event": self._interrupt_event})
        self._sending_thread.daemon = True
        self._sending_thread.start()

    def _send_status_data(self, interrupt_event, configuration):
        parameters = " ".join(configuration['monitoring_parameters'])
        interval = int(configuration['probing_interval'])

        time_difference = 0
        while not interrupt_event.wait(max(interval - time_difference, 0)):
            start_time = time.time()
            utils_functions.write_to_pipe(self.command_pipe, parameters)
            status_data = utils_functions.read_from_pipe(self.result_pipe)
            print(int(time.time()), status_data)

            url, headers, payload = self._form_status_data_request(status_data)
            try:
                response = requests.post(url, data=json.dumps(payload), headers=headers)
                print(response)
            except Exception:
                print("Record could not be sent")

            time_difference = time.time() - start_time

    def _form_status_data_request(self, status_data):
        url = "http://{}:{}/aps/JsonRequest".format(self.server_ip, self.server_port)
        headers = {"content-type": "aps/json"}
        payload = {"message": "monitoring_data",
                   "hostname": self.hostname,
                   "monitored_properties": json.loads(status_data),
                   }
        return url, headers, payload

    def stop_sending_data(self):
        if self._sending_thread is not None:
            self._interrupt_event.set()
            self._sending_thread.join()
