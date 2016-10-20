import time
from threading import Thread

from utils import utils_functions


class DataSender:
    def __init__(self, command_pipe, result_pipe):
        self._is_sending_data = False
        self._sending_thread = None
        self.command_pipe = command_pipe
        self.result_pipe = result_pipe

    def is_sending_data(self):
        return self._is_sending_data

    @staticmethod
    def register_on_server(server_ip, server_port, host_port):
        url = "http://{}:{}/aps/JsonRequest".format(server_ip, server_port)
        headers = {"content-type": "aps/json"}
        payload = {"message": "register", "listening_port": host_port}
        print("before authorization")
        return 200

    def start_sending_data(self, configuration):
        self._is_sending_data = True;
        self._sending_thread = Thread(target=self._send_status_data, kwargs={"configuration": configuration, })
        self._sending_thread.start()

    def _send_status_data(self, configuration):
        parameters = configuration['monitoring_parameters']
        interval = int(configuration['probing_interval'])

        while self._is_sending_data:
            start_time = time.time()
            utils_functions.write_to_pipe(self.command_pipe, parameters)
            result = utils_functions.read_from_pipe(self.result_pipe)
            print(result)

            time_difference = time.time() - start_time
            if time_difference < interval:
                time.sleep(interval - time_difference)

    def stop_sending_data(self):
        self._is_sending_data = False
        if self._sending_thread is not None:
            self._sending_thread.join()
