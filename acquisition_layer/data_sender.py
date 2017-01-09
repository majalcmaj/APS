import logging
import time

from acquisition_layer import ServerCommunicator
from configuration import settings
from configuration_managers.client_conifguration_manager import ClientConfigurationManager
from utils import utils

LOGGER = logging.getLogger("aps")


class DataSender:
    def __init__(self, key, command_pipe, result_pipe):
        self._key = key
        self.command_pipe = command_pipe
        self.result_pipe = result_pipe

        self._conf_mgr = ClientConfigurationManager()

    def start_sending_data(self):
        parameters = self._conf_mgr['monitoring_parameters']
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

                    # sending data
                    payload = {"monitored_properties": aggregator,
                               "key": str(self._key),
                               "timestamp": int(time.time())
                               }
                    result = ServerCommunicator.send_monitoring_data(
                        payload
                    )
                    if result == "ok":
                        LOGGER.info("Sent: " + str(aggregator))
                    elif result == "conf_changed":
                        self._conf_mgr.get_client_configuration_from_server()
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

                    counter -= 1
                    time_difference = time.time() - start_time
                    if settings.BASE_PROBING_INTERVAL - time_difference > 0:
                        time.sleep(settings.BASE_PROBING_INTERVAL - time_difference)
            except Exception:
                LOGGER.exception("An exception has ocurred during data sending")
