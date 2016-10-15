import json

import requests

from acquisition_presentation_server.models import Client


class ClientsConfigurator:
    @staticmethod
    def send_configuration(pk):
        client = Client.objects.get(pk=pk)
        url = "http://{}:{}".format(client.ip_address, 13000)
        headers = {"content-type": "aps/json"}
        payload = {
            "data_type": "configuration",
            "monitoring_parameters": "free_disk_space cpu_usage ram_usage",
            "probing_interval":"11"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print("Response: " + str(response))
        return response