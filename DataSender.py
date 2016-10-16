import requests
from threading import Thread
import time
import json
from HardwareDataCollector import HardwareDataCollector
import threading
import sched, time


class DataSender:
    def __init__(self):
        self.lock = threading.Lock()
        self._is_sending_data = False
        self._sending_thread = None
        self._sending_scheduler = None

    def is_sending_data(self):
        return self._is_sending_data

    @staticmethod
    def register_on_server(server_ip, server_port, host_port):
        url = "http://{}:{}/aps/JsonRequest".format(server_ip, server_port)
        headers = {"content-type": "aps/json"}
        payload = {"message": "register", "listening_port": host_port}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        return response.status_code
        # return 200

    def start_sending_data(self, server_ip, server_port, monitoring_parameters, probing_interval):
        self._is_sending_data = True;
        methods = HardwareDataCollector.map_names_onto_functions(monitoring_parameters)

        self._sending_thread = Thread(target=self._send_status_data,
                                      kwargs={"server_ip": server_ip,
                                              "server_port": server_port,
                                              "monitoring_methods": methods,
                                              "probing_interval": probing_interval,
                                              })
        self._sending_thread.start()

    def _send_status_data(self, server_ip, server_port, monitoring_methods, probing_interval):
        while self._is_sending_data:
            starttime = time.time()
            status = {}
            for method in monitoring_methods:
                status[method[0]] = method[1]()
            print(status)
            time.sleep(probing_interval - (time.time() - starttime))

    def stop_sending_data(self):
        self._is_sending_data = False
        if self._sending_thread is not None:
            self._sending_thread.join()
