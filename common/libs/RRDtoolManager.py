import os
import rrdtool
import time
import logging

from APS import settings
from APS.settings import LOGGER_NAME

LOGGER = logging.getLogger(LOGGER_NAME)


# TODO: Artur komentarze
def create_rrd(client):
    rrd_database_name = _get_rrd_abs_path(client.pk)
    database_update_frequency = client.consecutive_probes_sent_count * client.base_probing_interval
    monitoring_parameters = []
    for mp in client.monitored_properties.filter(monitored=True):
        if mp.type != 'string':
            monitoring_parameters.append(
                "DS:" + mp.name + ":GAUGE:" + str(2 * database_update_frequency) + ":U:U")

    database_probes_count = int(client.monitoring_timespan /
                                (client.base_probing_interval *
                                 client.consecutive_probes_sent_count))
    rrd_archives = ["RRA:AVERAGE:0.99:1:{}".format(database_probes_count)]

    command = [rrd_database_name,
               '--start', str(int(time.time())),
               '--step', str(database_update_frequency)]

    for monitoring_parameter in monitoring_parameters:
        command.append(monitoring_parameter)
    for rrd_archive in rrd_archives:
        command.append(rrd_archive)

    LOGGER.debug("RRD create command: %s" % command)
    rrdtool.create(command)


def update_rrd(client, records, time):
    rrd_database_name = _get_rrd_abs_path(client.pk)
    record_string = str(time)
    template_string = ""
    for k, v in records.items():
        template_string += ":" + k
        record_string += ":" + str(v)

    try:
        rrdtool.update(rrd_database_name, '--template', template_string[1:], record_string)
    except Exception as e:
        LOGGER.exception("Records could not be writtend into database.")


def fetch_data(client, since):
    rrd_database_name = _get_rrd_abs_path(client.pk)
    records = rrdtool.fetch(rrd_database_name, 'AVERAGE', '-a', '--start', str(since))
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
        LOGGER.debug("RRD fetch result: %s" % result)
    return result, times[1]


def _get_rrd_abs_path(client_pk):
    return os.path.join(settings.RRD_DATABASE_DIRECTORY, "{}.rrd".format(client_pk))
