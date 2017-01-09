import psutil

VALUE_UNIT = "MB"


def read_value():
    return round(psutil.virtual_memory().available / 1000**2, 2)
