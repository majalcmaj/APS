import json
import socketserver
from ConfigurationReceiverHandler import ConfigurationReceiverHandler
from DataSender import DataSender

class ConfigurationReceiver(socketserver.TCPServer):
    def __init__(self):
        self._load_initial_configuration()
        self.data_sender = DataSender()
        socketserver.TCPServer.__init__(self, ("", int(self._server_port)), ConfigurationReceiverHandler)

    def get_sending_thread(self):
        return self.sending_thread

    def run(self):
        response = DataSender.register_on_server(self._server_ip, self._server_port,self._host_port)
        if response is 200:
            self.serve_forever()

    def _load_initial_configuration(self):
        with open("config.json") as configuration_file:
            configuration = json.load(configuration_file)
            self._server_ip = configuration["SERVER_IP"]
            self._server_port = configuration["SERVER_PORT"]
            self._hostname = configuration["HOST_NAME"]
            self._host_ip = configuration["HOST_IP"]
            self._host_port = configuration["HOST_PORT"]
            self._type = configuration["TYPE"]

    def get_server_ip(self):
        return self._server_ip

    def get_server_port(self):
        return self._server_port


if __name__ == '__main__':
    receiver = ConfigurationReceiver();
    receiver.run()
