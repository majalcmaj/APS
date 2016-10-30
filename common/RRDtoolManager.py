import rrdtool
import time

from acquisition_presentation_server import settings


class RRDtoolManager:
    def __init__(self, client):
        self._path = settings.RRD_DATABASE_DIRECTORY
        self._hostname = client.hostname
        self._monitored_properties = {property.name: property.type for property in client.monitored_properties.all()}
        self._probing_interval = client.probing_interval

    def create_rrd(self):
        rrd_database_name = self._get_rrd_abs_path()
        monitoring_parameters = []
        for k, v in self._monitored_properties.items():
            if v != 'string':
                monitoring_parameters.append("DS:" + k + ":GAUGE:" + str(2 * self._probing_interval) + ":U:U")

        rrd_archives = []
        rrd_archives.append("RRA:AVERAGE:0.5:1:120")

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
        record_string = str(int(time.time()))
        template_string = ""
        for k, v in records.items():
            template_string += ":" + k
            record_string += ":" + v

        rrdtool.update(rrd_database_name, '--template', template_string[1:], record_string)

    def update_rrd_with_order(self, records):
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

    #TODO: To trzeba poprawić dobrze. Nie mam pojęcia jak, moje tymczasowe rozwiązanie jest do dupy.
    def fetch_data(self, time_period):
        rrd_database_name = self._get_rrd_abs_path()

        current_time = int(time.time())
        records = rrdtool.fetch(rrd_database_name, 'LAST', '--start', str(current_time - time_period))
        result = {}
        data = result['data'] = {}
        order = records[1]
        data_tuples = records[2]
        data_tuples = list(filter(lambda tup: None not in tup, data_tuples))
        start_time = records[0][0]
        interval = records[0][2]
        unix_times = [start_time + i * interval for i in range(0, len(data_tuples))]
        result['unix_time'] = unix_times
        last_not_null_time = unix_times[-1]
        for i in range(0, len(order)):
            data[order[i]] = [value[i] for value in data_tuples]

        return result, last_not_null_time
        # rrd_database_name = self._get_rrd_abs_path()
        #
        # current_time = int(time.time())
        # records = rrdtool.fetch(rrd_database_name, 'LAST', '--start', str(current_time - time_period), '--end',
        #                         str(current_time))
        # result = {}
        # result['unix_time'] = [current_time - time_period + i for i in range(1, len(records[2]) + 1)]
        # data = result['data'] = {}
        # order = records[1]
        # for i in range(0, len(order)):
        #     data[order[i]] = [value[i] for value in records[2]]
        # return result
