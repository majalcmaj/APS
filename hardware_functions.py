import subprocess
import psutil
import socket

# add functions for monitoring parameters
# result should be a string
# format : get_parameter_name():

def get_cpu_usage():
    return str(psutil.cpu_percent())


def get_ram_usage():
    return str(round(psutil.virtual_memory().available / 1024 / 1024, 2))


def get_hostname():
    return socket.gethostname()


def get_free_disk_space():
    return str(round(psutil.disk_usage("/").free / 1024 / 1024, 2))

def get_not_found_parameter():
    return "not found"
