from acquisition_presentation_server.models import Client
from acquisition_presentation_server.common.RRDtoolManager import RRDtoolManager
import time


class ManageMonitoringData:
    @staticmethod
    def process_data(ip_address, records):
        print(ip_address, records)
        client = Client.objects.get(ip_address=ip_address)
        RRDtoolManager(client).update_rrd(records)
        client.last_update = int(time.time())
        client.save()
