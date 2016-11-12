import signal
import sys


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
        print("\nClient has finished")
        sys.exit(0)
