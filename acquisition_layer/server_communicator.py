import json
import logging

import requests
import time

from requests.packages.urllib3.exceptions import NewConnectionError

from configuration.constant_values import MESSAGE_DATA_DELIMITER
from utils.utils import CryptUtils

logger = logging.getLogger("aps")


class ServerCommunicator:
    def __init__(self, conf_manager):
        self._conf_mgr = conf_manager
        base_url = "http://{0}:{1}/aps_client/".format(
            conf_manager["SERVER_IP"],
            conf_manager["SERVER_PORT"],
        )
        self._urls = {
            "MONITORING_DATA": base_url + "monitoring_data",
            "CLIENT_IDENTITY": base_url + "client_identity",
            "CLIENT_CONFIGURATION": base_url + "client_configuration",
        }
        self._header = {"content-type": "aps/json"}

    def send_monitoring_data(self, data):
        try:
            status, _ = self._send_data(
                requests.put,
                "MONITORING_DATA",
                data
            )
            if status is not None:
                if status == 200:
                    return "ok"
                elif status == 303:
                    logger.info("The configuration of client has been altered, attempting to download")
                    while True:
                        try:
                            self._conf_mgr.get_client_configuration_from_server()
                            if self._conf_mgr.is_configured_by_server():
                                break
                        except Exception:
                            logger.exception("An exception has ocurred during configuration acquiring.")
                        time.sleep(5)

                    return "conf_changed"
                else:
                    logger.error("Sending monitoring data failed with code {}".format(
                        status
                    ))
        except (requests.ConnectionError):
            logger.exception("A connection error has ocurred during data sending.")
        except Exception:
            logger.exception("An exception has ocurred during data sending.")
        return None

    def validate_client_identity(self, client_key):
        try:
            status, _ = self._send_data(requests.get, "CLIENT_IDENTITY", {"key": str(client_key)})
            if status is not None:
                if status == 200:
                    return True
                elif status == 404:
                    logger.info("Client id not found on server, attempting to register anew")
                    # ! ClientConfigurationHandler.get_client_configuration_from_server()
                    return True
                else:
                    logger.error("Validation of client's identity failed with code {}".format(
                        status
                    ))
        except (requests.ConnectionError, NewConnectionError):
            logger.error("Could not connect to server")
        except Exception:
            logger.exception("An exception has ocurred during data sending.")
        finally:
            return None

    def register_client(self, data):
        try:
            status, data = self._send_data(requests.post, "CLIENT_IDENTITY", data)
            if status is not None:
                if status == 200:
                    return json.loads(data, encoding="UTF-8")["key"]
                else:
                    logger.error("Client registration failed with code {}".format(
                        status
                    ))
        except (requests.ConnectionError, NewConnectionError):
            logger.error("Could not connect to server.")
        except Exception:
            logger.exception("An exception has ocurred during data sending.")
        return None

    def get_client_configuration(self, key):
        try:
            status, data = self._send_data(
                requests.get,
                "CLIENT_CONFIGURATION",
                {"key": key}
            )
            if status is not None:
                if status == 200:
                    return json.loads(data, encoding="UTF-8")
                elif status == 202:
                    logger.info("No client configuration set on server yet.")
                else:
                    logger.error("Attempt to get configuration failed with code {}.".format(
                        status
                    ))
        except requests.ConnectionError:
            logger.error("A connection error has ocurred during data sending.")
        except Exception:
            logger.exception("An exception has ocurred during data sending.")
        return {}

    def _send_data(self, request_method, type, data):
        # For digital signature purrpose
        data_json = json.dumps(data, sort_keys=True, encoding='UTF-8')
        data_json = CryptUtils.create_signature(data_json) + MESSAGE_DATA_DELIMITER + data_json
        # Prepare data - digital sign
        response = request_method(
            url=self._urls[type],
            data=data_json,
            headers=self._header
        )
        try:
            digest, data = response._content.split(MESSAGE_DATA_DELIMITER)
            is_correct = CryptUtils.validate_signature(
                data=data,
                signature=digest
            )
            if is_correct:
                return response.status_code, data.decode("UTF-8")
            else:
                logger.error("Digital signature verification failed.")
        except ValueError:
            logger.error("No digital signature in response!")
        except Exception:
            logger.exception("Exception has ocurred during data receiving.")
        return None, None
