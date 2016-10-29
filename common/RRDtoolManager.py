import rrdtool
import time

from acquisition_presentation_server import settings


class RRDtoolManager:

    def __init__(self, client):
        self._path = settings.RRD_DATABASE_DIRECTORY
        self._hostname = client.hostname
        self._monitored_properties = {property.name:property.type for property in client.monitored_properties.all()}
        self._probing_interval = client.probing_interval

    def create_rrd(self):
        rrd_database_name = self._get_rrd_abs_path()
        monitoring_parameters = []
        for k, v in self._monitored_properties.items():
            if v != 'string':
                monitoring_parameters.append("DS:" + k + ":GAUGE:" + str(2 * self._probing_interval) + ":U:U")

        rrd_archives = []
        rrd_archives.append("RRA:LAST:0.5:1:120")

        command = []
        command.append(rrd_database_name)
        command.append('--start')
        command.append(str(int(time.time())))
        command.append('--step')
        command.append(str(self._probing_interval))

        for monitoring_parameter in monitoring_parameters:
            command.append(monitoring_parameter)
        for rrd_archive in rrd_archives:
            command.append(rrd_archive)

        rrdtool.create(command)

    def update_rrd(self, records):
        rrd_database_name = self._get_rrd_abs_path()
        order = self._retreive_order_of_rows(rrd_database_name)
        record_string = str(int(time.time()))
        for record in order:
            record_string += ":" + records[record]

        # print(record_string)
        rrdtool.update(rrd_database_name, record_string)

    # TODO Nie da się inaczej, niż czytać plik
    # dla paru klientów ok, ale jak z 50 co sekundę to może być wąskie gardło


    def _retreive_order_of_rows(self, path):
        params = []
        for k, v in rrdtool.info(path).items():
            if k.find('].index') != -1:
                params.append((k[k.find('[') + 1:k.rfind(']')], v))
        params.sort(key=lambda tup: tup[1])
        return [param[0] for param in params]

    def _get_rrd_abs_path(self):
        return self._path + "/" + self._hostname + ".rrd"

    # TODO Czy da się pobierać tylko jedną daną?
    def fetch_data(self, time_period):
        rrd_database_name = self._get_rrd_abs_path()

        current_time = int(time.time())
        records = rrdtool.fetch(rrd_database_name, 'LAST', '--start', str(current_time-time_period), '--end',
                                str(current_time))
        result = {}
        result['unix_time'] = [current_time-time_period + i for i in range(1, len(records[2]) + 1)]
        data = result['data'] = {}
        order = self._retreive_order_of_rows(rrd_database_name)
        for i in range(0, len(order)):
            data[order[i]] = [value[i] for value in records[2]]
        return result
