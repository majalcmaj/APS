import signal
import sys
import os
import logging
from configuration.constant_values import LOGGING_BASE_FILE,LOGGING_TEMP_FILE

class InterruptHandler:
    def __init__(self):
        self.tcp_server = None

    def set_tcp_server(self, tcp_server):
        self.tcp_server = tcp_server

    def register_interrupt_handler(self):
        signal.signal(signal.SIGINT, self._exit_method)

    def _exit_method(self, signal, frame):
        if self.tcp_server is not None:
            self.tcp_server.shutdown()

        #saving log files
        logging.getLogger("aps").handlers[0].close()
        if os.path.exists(LOGGING_BASE_FILE):
            log = open(LOGGING_BASE_FILE, 'a')
            if os.path.exists(LOGGING_TEMP_FILE):
                tmp = open(LOGGING_TEMP_FILE, 'r')
                log.write(tmp.read())
                tmp.close()
                os.remove(LOGGING_TEMP_FILE)
            log.close()
        elif os.path.exists(LOGGING_TEMP_FILE):
            os.rename(LOGGING_TEMP_FILE, LOGGING_BASE_FILE)

        print("\nClient has finished")
        sys.exit(0)
