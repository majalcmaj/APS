import time
import calendar

# TO trzeba zamienić na wywołanie funkcji rrd, musi zwracać taki sam output
from acquisition_presentation_server.common.RRDtoolManager import RRDtoolManager

def get_client_data(client, time_period):
    return RRDtoolManager(client).fetch_data(time_period)
