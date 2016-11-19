# TO trzeba zamienić na wywołanie funkcji rrd, musi zwracać taki sam output
from acquisition_presentation_server.common import RRDtoolManager

def get_client_data(client, since):
    return RRDtoolManager.fetch_data(client, since)

def get_client_alerts(client):
    return [alert.created + ": " + alert.message for alert in client.alerts.all()]