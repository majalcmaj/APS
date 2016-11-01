from http.server import SimpleHTTPRequestHandler
import json
import constant_values


class ConfigurationReceiverHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        length = self.headers['content-length']
        data = self.rfile.read(int(length))
        configuration = json.loads(data.decode('utf-8'))

        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()

        self.configure_client(configuration)
        self.save_current_conifguration(configuration)

    def configure_client(self, configuration):
        if configuration['data_type'] == 'configuration':
            self.server.data_sender.stop_sending_data()
            self.server.data_sender.start_sending_data(configuration)

    def save_current_conifguration(self, configuration):
        with open(constant_values.LAST_CONFIG_PATH, 'w') as file:
            json.dump(configuration, file)
