import hashlib
import hmac
import json
import logging
import os, pwd, grp
import socket
from logging.handlers import RotatingFileHandler

from configuration import settings
from configuration.settings import LOGGING_TEMP_FILE, DIGITAL_SIGNATURE_SECRET


def read_from_pipe(pipe):
    message = bytearray()
    while True:
        data = os.read(pipe, 1)
        if data == b'\0':
            return json.loads(str(message).decode("UTF-8"))
        else:
            message.append(data)


def write_to_pipe(pipe, data):
    data = json.dumps(data) + b'\0'
    os.write(pipe, data.encode("UTF-8"))


def drop_privileges(uid_name, gid_name):
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    os.setgroups([])

    os.setgid(running_gid)
    os.setuid(running_uid)


def yes_no_prompt(question):
    yes_options = ['yes', 'y', '']
    print(question)
    choice = input()

    if choice.lower() in yes_options:
        return True
    else:
        return False


def get_hostname():
    return socket.gethostname()


class MyRotatingHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, encoding=None, delay=0):
        RotatingFileHandler.__init__(self, LOGGING_TEMP_FILE, mode, maxBytes, 1, encoding, delay)
        self.custom_name = filename

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        destiny_filename = self.custom_name
        if os.path.exists(destiny_filename):
            os.remove(destiny_filename)
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, destiny_filename)

        self.stream = self._open()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class CryptUtils:
    @staticmethod
    def create_signature(data):
        return hmac.new(DIGITAL_SIGNATURE_SECRET, data, hashlib.sha256).digest()

    @staticmethod
    def validate_signature(data, signature):
        return hmac.compare_digest(
            CryptUtils.create_signature(data),
            signature
        )


def setup_logger():
    logger = logging.getLogger(settings.LOGGER_NAME)
    logger.setLevel(settings.LOGGING_LEVEL)
    handler = logging.StreamHandler()  # MyRotatingHandler(constant_values.LOGGING_BASE_FILE, maxBytes=10 * 1024 * 1024)
    formatter = logging.Formatter(settings.LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
