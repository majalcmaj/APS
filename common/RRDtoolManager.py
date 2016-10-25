import rrdtool
import time

class RRDtoolManager:
    def __init__(self, client):
        self._path = client.rrd_database_location
        self._monitored_properties = {property.name:property.type for property in client.monitored_properties.all()}
        self._probing_interval = client.probing_interval

    def create_rrd(self):
        monitoring_parameters = []
        for k, v in self._monitored_properties.items():
            if v != 'string':
                monitoring_parameters.append("DS:" + k + ":GAUGE:" + str(2 * self._probing_interval) + ":U:U")

        rrd_archives = ["RRA:LAST:0.5:1:120"]

        command = [self._path,
                   '--start', str(int(time.time())),
                   '--step', str(self._probing_interval)]

        for monitoring_parameter in monitoring_parameters:
            command.append(monitoring_parameter)
        for rrd_archive in rrd_archives:
            command.append(rrd_archive)

        rrdtool.create(command)

    def update_rrd(self, data):
        records = data.keys()
        record_string = str(int(time.time()))
        record_string += ":" + ":".join(data[record] for record in data)

        print(record_string)
        rrdtool.update(self._path, record_string,
                       "-t", ":".join(records))

    def fetch_data(self, seconds_span):
        end_time = int(time.time())
        start_time = end_time - seconds_span
        records = rrdtool.fetch(self._path, 'LAST', '--start', str(start_time), '--end',
                                str(end_time))
        print(records)
        time_info = records[0]
        print(time_info)
        result = {'time': list(range(time_info[0], time_info[1], time_info[2]))}
        print(result)
        for idx in range(0, len(records[1])):
            vals = [value[idx] for value in records[2]]
            result[records[1][idx]] = vals
        return result
