import rrdtool
import time

from acquisition_presentation_server import settings
from acquisition_presentation_server.models import Client


class RRDtoolManager:
    def __init__(self, client):
        self._path = settings.RRD_DATABASE_DIRECTORY
        self._hostname = client.hostname
        self._monitored_properties = {
            prop.name: prop.type
            for prop in client.monitored_properties.filter(monitored=True)
            }
        self._probing_cycles = client.probing_interval
        self._base_probing_interval = client.base_probing_interval
        self._client_pk = client.pk

    def create_rrd(self):
        if len(self._monitored_properties) > 0:
            rrd_database_name = self._get_rrd_abs_path()
            monitoring_parameters = []
            for k, v in self._monitored_properties.items():
                if v != 'string':
                    monitoring_parameters.append(
                        "DS:" + k + ":GAUGE:" + str(2 * self._probing_cycles * self._base_probing_interval) + ":U:U")

            rrd_archives = []
            rrd_archives.append("RRA:AVERAGE:0.5:1:120")

            command = []
            command.append(rrd_database_name)
            command.append('--start')
            command.append(str(int(time.time())))
            command.append('--step')
            command.append(str(self._probing_cycles * self._base_probing_interval))

            for monitoring_parameter in monitoring_parameters:
                command.append(monitoring_parameter)
            for rrd_archive in rrd_archives:
                command.append(rrd_archive)

            rrdtool.create(command)

    def update_rrd(self, records):
        if len(self._monitored_properties) > 0:
            rrd_database_name = self._get_rrd_abs_path()
            record_string = str(int(time.time()))
            template_string = ""
            for k, v in records.items():
                template_string += ":" + k
                record_string += ":" + v

            rrdtool.update(rrd_database_name, '--template', template_string[1:], record_string)

    def update_rrd_with_order(self, records):
        if len(self._monitored_properties) > 0:
            rrd_database_name = self._get_rrd_abs_path()
            order = self._retreive_order_of_rows(rrd_database_name)
            record_string = str(int(time.time()))
            for record in order:
                record_string += ":" + records[record]
            rrdtool.update(rrd_database_name, record_string)

    @staticmethod
    def _retreive_order_of_rows(path):
        params = []
        for k, v in rrdtool.info(path).items():
            if k.find('].index') != -1:
                params.append((k[k.find('[') + 1:k.rfind(']')], v))
        params.sort(key=lambda tup: tup[1])
        return [param[0] for param in params]

    def _get_rrd_abs_path(self):
        return self._path + "/" + self._hostname + ".rrd"

    def fetch_data(self, time_period):
        rrd_database_name = self._get_rrd_abs_path()
        records = rrdtool.fetch(rrd_database_name, 'AVERAGE', '--start', str(int(time.time()) - time_period))
        start, end, step = records[0]
        times = list(range(start, end, step))
        client = Client.objects.get(pk=self._client_pk)
        record_omits = 2 if client.last_update < times[-1] else 1

        result = {}
        result['unix_time'] = times[:-record_omits]
        data = result['data'] = {}
        order = records[1]
        for i in range(0, len(order)):
            data[order[i]] = [value[i] for value in records[2]]
            data[order[i]] = data[order[i]][:-record_omits]
        return result, times[-1]
