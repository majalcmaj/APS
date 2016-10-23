import rrdtool
import json
import time

class RRDtoolManager:
    def __init__(self, client):
        self._hostname = client.hostname
        self._parameters = {prop.name:prop.type for prop in client.monitored_properties.all()}
        self._probing_interval = client.probing_interval
        self._path = client.rrd_database_location

    def create_rrd(self):
        rrd_database_name = self._path
        monitoring_parameters = []
        for k, v in self._parameters.items():
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
        order = self._retreive_order_of_rows(self._path)

        record_string = str(int(time.time()))

        for record in order:
            record_string += ":" + records[record]

        #TODO IDE krzyczy - O co chodzi?
        rrdtool.update(self._path, record_string)

    # TODO Zamienić to naopcję template dla rrd_update http://oss.oetiker.ch/rrdtool/doc/rrdupdate.en.html
    def _retreive_order_of_rows(self, path):
        params = []
        for k, v in rrdtool.info(path).items():
            if k.find('].index') != -1:
                params.append((k[k.find('[') + 1:k.rfind(']')], v))
        params.sort(key=lambda tup: tup[1])
        return [param[0] for param in params]

    def fetch_data(self,start_time, end_time):

        records = rrdtool.fetch(self._path, 'LAST', '--start', str(start_time), '--end',
                                str(end_time))
        result = {}
        result['time'] = [start_time + i for i in range(1, len(records[2]) + 1)]

        #TODO - patrz wyżej
        order = self._retreive_order_of_rows(self._path)
        for i in range(0, len(order)):
            result[order[i]] = [value[i] for value in records[2]]
        return result