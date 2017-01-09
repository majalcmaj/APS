import grp
import hashlib
import hmac
import logging
import os
import pwd
import socket
from logging.handlers import RotatingFileHandler

from configuration import settings
from configuration.settings import LOGGING_TEMP_FILE, DIGITAL_SIGNATURE_SECRET


def drop_privileges(uid_name, gid_name):
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    os.setgroups([])

    os.setgid(running_gid)
    os.setuid(running_uid)


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
