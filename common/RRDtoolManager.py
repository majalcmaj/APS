import os
import rrdtool
import time

from acquisition_presentation_server import settings


def create_rrd(client):
    rrd_database_name = _get_rrd_abs_path(client.pk)
    database_update_frequency = client.probing_interval * client.base_probing_interval
    monitoring_parameters = []
    for mp in client.monitored_properties.filter(monitored=True):
        if mp.type != 'string':
            monitoring_parameters.append(
                "DS:" + mp.name + ":GAUGE:" + str( 2 * database_update_frequency) + ":U:U")

    rrd_archives = ["RRA:AVERAGE:0.99:1:120"]

    command = [rrd_database_name,
               '--start', str(int(time.time())),
               '--step', str(database_update_frequency)]

    for monitoring_parameter in monitoring_parameters:
        command.append(monitoring_parameter)
    for rrd_archive in rrd_archives:
        command.append(rrd_archive)

    rrdtool.create(command)


def update_rrd(client, records, time):
    rrd_database_name = _get_rrd_abs_path(client.pk)
    record_string = str(time)
    template_string = ""
    for k, v in records.items():
        template_string += ":" + k
        record_string += ":" + str(v)

    rrdtool.update(rrd_database_name, '--template', template_string[1:], record_string)


# def fetch_data(client, since):
#     rrd_database_name = _get_rrd_abs_path(client.pk)
#     records = rrdtool.fetch(rrd_database_name, 'AVERAGE', '--start', str(since))
#     records_count = len(records[2])
#     if records_count == 0:
#         return None, None
#     else:
#         # start, end, step = records[0]
#         # times = list(range(start, end, step))
#
#         result = {'unix_time': records[0]}
#         data = {}
#         order = records[1]
#         for i in range(0, len(order)):
#             records_array = [value[i] for value in records[2]]
#             data[order[i]] = records_array
#
#         result['data'] = data
#         return result, records[0][1]

def fetch_data(client, since):
    rrd_database_name = _get_rrd_abs_path(client.pk)
    records = rrdtool.fetch(rrd_database_name, 'AVERAGE', '-a', '--start', str(since))
    # start, end, step = records[0]
    # #times = list(range(start, end, step))
    times = list(records[0])
    record_omits = 2 if client.last_update < times[1] else 1

    result = {}
    times[1] -= record_omits * times[2]
    result['unix_time'] = times
    data = result['data'] = {}
    order = records[1]
    for i in range(0, len(order)):
        data[order[i]] = [value[i] for value in records[2]]
        data[order[i]] = data[order[i]][:-record_omits]
    print(result)
    return result, times[1]


def _get_rrd_abs_path(client_pk):
    return os.path.join(settings.RRD_DATABASE_DIRECTORY, "{}.rrd".format(client_pk))
