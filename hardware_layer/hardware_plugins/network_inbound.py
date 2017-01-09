import psutil
import time

VALUE_UNIT = "kb/s"


class ValuesContainer:
    last_time = None
    last_value = None


def get_total_inbound():
    return round(psutil.net_io_counters().bytes_recv / 1000, 2)


def read_value():
    if ValuesContainer.last_time is None:
        ValuesContainer.last_time = int(time.time())
        ValuesContainer.last_value = get_total_inbound()
        return 0
    else:
        curr_time = int(time.time())
        curr_value = get_total_inbound()
        dt = curr_time - ValuesContainer.last_time
        if dt == 0:
            return 0
        result = round(float(curr_value - ValuesContainer.last_value) / dt, 2)
        ValuesContainer.last_value = curr_value
        ValuesContainer.last_time = curr_time
        return result
