import os, pwd, grp
from logging.handlers import RotatingFileHandler
from configuration.constant_values import LOGGING_TEMP_FILE

def read_from_pipe(pipe):
    message = b''
    while True:
        data = os.read(pipe, 1)
        if data == b'\0':
            return message.decode('utf-8')
        else:
            message += data


def write_to_pipe(pipe, data):
    os.write(pipe, (data + "\0").encode('utf-8'))


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
