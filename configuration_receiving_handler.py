from http.server import SimpleHTTPRequestHandler
import json
from threading import Thread


class ConfigurationReceiverHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        length = self.headers['content-length']
        data = self.rfile.read(int(length))

        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()

        self.configure_client(data)

    def configure_client(self, data):
        configuration = json.loads(data.decode('utf-8'))
        if configuration['data_type'] == 'configuration':
            self.server.data_sender.stop_sending_data()
            self.server.data_sender.start_sending_data(configuration)
