import time

from utils import utils
import requests
import json
import logging

LOGGER = logging.getLogger("aps")


class DataSender:
    def __init__(self, command_pipe, result_pipe, configuration_manager, server_communicator):
        self.command_pipe = command_pipe
        self.result_pipe = result_pipe

        self._key = None
        self._conf_mgr = configuration_manager
        self._server_communicator = server_communicator

    def set_key(self, key):
        self._key = key

    def start_sending_data(self):
        parameters = self._conf_mgr['monitoring_parameters']
        base_probing_interval = int(self._conf_mgr["BASE_PROBING_INTERVAL"])

        counter = int(self._conf_mgr['probing_interval'])
        aggregator = {}
        for p in parameters:
            aggregator[p] = 0

        while True:
            # Wrapping in try/except, so the process won't fail, no matter what the exceptions
            try:
                if counter == 0:
                    divider = int(self._conf_mgr['probing_interval'])

                    for k, v in aggregator.items():
                        aggregator[k] = round(v / divider, 2)

                    LOGGER.info("Connected to server")
                    # sending data
                    payload = {"message": "monitoring_data",
                               "monitored_properties": aggregator,
                               "key": str(self._key),
                               "timestamp": int(time.time())
                               }
                    result = self._server_communicator.send_monitoring_data(
                        payload
                    )
                    if result != "ok":
                        if result == "conf_changed":
                            parameters = self._conf_mgr['monitoring_parameters']
                            aggregator = {}
                    for key in parameters:
                        aggregator[key] = 0
                    counter = int(self._conf_mgr['probing_interval'])

                else:
                    start_time = time.time()
                    utils.write_to_pipe(self.command_pipe, parameters)
                    status_data = utils.read_from_pipe(self.result_pipe)
                    for k, v in status_data.items():
                        aggregator[k] += float(v)

                    LOGGER.info(status_data)

                    counter -= 1
                    time_difference = time.time() - start_time
                    if base_probing_interval - time_difference > 0:
                        time.sleep(base_probing_interval - time_difference)
            except Exception:
                LOGGER.exception("An exception has ocurred during data sending")