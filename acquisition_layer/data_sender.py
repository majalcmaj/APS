import logging
import time

from acquisition_layer import ServerCommunicator
from configuration import settings

LOGGER = logging.getLogger(settings.LOGGER_NAME)


class DataSender:
    def __init__(self, conf_mgr, pipe):
        self._conf_mgr = conf_mgr
        self._key = conf_mgr.key
        self._pipe = pipe

    def start_sending_data(self):
        parameters = self._conf_mgr.plugins_available
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
                    self._pipe.send(parameters)
                    status_data = self._pipe.recv()
                    for k, v in status_data.items():
                        aggregator[k] += float(v)

                    counter -= 1
                    time_difference = time.time() - start_time
                    if settings.BASE_PROBING_INTERVAL - time_difference > 0:
                        time.sleep(settings.BASE_PROBING_INTERVAL - time_difference)
            except Exception:
                LOGGER.exception("An exception has ocurred during data sending")
