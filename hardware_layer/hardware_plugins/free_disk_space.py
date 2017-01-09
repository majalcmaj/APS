import psutil

VALUE_UNIT = "MB"


def read_value():
    return round(psutil.disk_usage("/").free / 1000**2, 2)
