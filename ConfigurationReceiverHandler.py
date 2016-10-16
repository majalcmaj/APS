from http.server import SimpleHTTPRequestHandler
import json


class ConfigurationReceiverHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        length = self.headers['content-length']
        data = self.rfile.read(int(length))

        data_type, monitoring_parameters,probing_interval = self._parse_configuration_json(data)
        if data_type == 'configuration':
            self.server.data_sender.stop_sending_data()
            self.server.data_sender.start_sending_data(self.server.get_server_ip(), self.server.get_server_port(),
                                                       monitoring_parameters,probing_interval)

        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()

    def _parse_configuration_json(self, data):
        json_data = json.loads(data.decode('utf-8'))
        data_type = json_data["data_type"]
        probing_interval= json_data["probing_interval"]
        if data_type == "configuration":
            monitoring_parameters = json_data["monitoring_parameters"].split(" ")
            # print(monitoring_parameters)

        return data_type, monitoring_parameters, int(probing_interval)
