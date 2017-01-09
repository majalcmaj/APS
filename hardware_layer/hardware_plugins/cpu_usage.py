import psutil

VALUE_UNIT = "%"


def read_value():
    return psutil.cpu_percent()
