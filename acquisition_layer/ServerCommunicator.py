import itertools
import json
import logging
import socket
import time

import requests
from requests.exceptions import ConnectionError

from configuration import settings
from utils.utils import CryptUtils

LOGGER = logging.getLogger("aps")


def send_monitoring_data(data):
    try:
        status, _ = _send_data(
            requests.put,
            settings.MONITORING_DATA_URL,
            data,
            retries_limit=3
        )
        if status is not None:
            if status == 200:
                return "ok"
            elif status == 303:
                LOGGER.info("The configuration of client has been altered, attempting to download")
                return "conf_changed"
            else:
                LOGGER.error("Sending monitoring data failed with code {}".format(
                    status
                ))
    except requests.ConnectionError:
        LOGGER.exception("A connection error has ocurred during data sending.")
    except Exception:
        LOGGER.exception("An exception has ocurred during data sending.")
    return None


def validate_client_identity(client_key):
    try:
        status, _ = _send_data(
            requests.post,
            settings.CLIENT_IDENTITY_URL,
            {"key": str(client_key)}
        )
        if status is not None:
            if status == 200:
                return True
            elif status == 404:
                LOGGER.info("Client id not found on server, attempting to register anew")
                # ClientConfigurationHandler.get_client_configuration_from_server()
                return False
            else:
                LOGGER.error("Validation of client's identity failed with code {}".format(
                    status
                ))
    except requests.ConnectionError:
        LOGGER.error("Could not connect to server")
    except Exception:
        LOGGER.exception("An exception has ocurred during data sending.")
    return False


def register_client():
    try:
        payload = {
            "monitored_properties": settings.MONITORED_PROPERTIES,
            "hostname": socket.gethostname(),
            "base_probing_interval": settings.BASE_PROBING_INTERVAL
        }
        status, data = _send_data(
            requests.get,
            settings.CLIENT_IDENTITY_URL,
            payload
        )

        if status is not None:
            if status == 200:
                return json.loads(data, encoding="UTF-8")["key"]
            else:
                LOGGER.error("Client registration failed with code {}".format(
                    status
                ))
                return None
    except requests.ConnectionError:
        LOGGER.error("Could not connect to server.")
    except Exception:
        LOGGER.exception("An exception has ocurred during data sending.")
    return None


def get_client_configuration(key):
    while True:
        try:
            status, data = _send_data(
                requests.get,
                settings.CLIENT_CONFIGURATION_URL,
                {"key": key}
            )
            if status is not None:
                if status == 200:
                    return json.loads(data, encoding="UTF-8")
                elif status == 202:
                    LOGGER.info("No client configuration set on server yet.")
                else:
                    LOGGER.error("Attempt to get configuration failed with code {}.".format(
                        status
                    ))
        except requests.ConnectionError:
            LOGGER.error("A connection error has ocurred during data sending.")
        except Exception:
            LOGGER.exception("An exception has ocurred during data sending.")
        time.sleep(10)


def _send_data(request_method, url, data, timeout=10, retries_limit=None):
    # For digital signature purrpose
    data_json = json.dumps(data, sort_keys=True, encoding='UTF-8')
    data_json = CryptUtils.create_signature(data_json) + settings.MESSAGE_DATA_DELIMITER + data_json
    # Prepare data - digital sign
    response = None
    for counter in itertools.count():
        if counter == retries_limit:
            LOGGER.warn("Max amount of sending attempts exceeded.")
            raise requests.Timeout()
        try:
            response = request_method(
                url,
                data=data_json,
                headers=settings.CUSTOM_APP_HEADER,
                timeout=timeout
            )
            break
        except requests.Timeout:
            LOGGER.error("A timeout od {} seconds has ocurred during data sending.".format(timeout))
            pass
        except Exception as e:
            if isinstance(e, ConnectionError):
                LOGGER.error("Could not connect to the server. Message: {}".format(e.message))
            else:
                LOGGER.exception('An exception has ocurred during connecting with server')
            time.sleep(timeout)

    try:
        digest, data = response._content.split(settings.MESSAGE_DATA_DELIMITER)
        is_correct = CryptUtils.validate_signature(
            data=data,
            signature=digest
        )
        if is_correct:
            return response.status_code, data.decode("UTF-8")
        else:
            LOGGER.error("Digital signature verification failed.")
    except ValueError:
        LOGGER.error("No digital signature in response!")
    except Exception:
        LOGGER.exception("Exception has ocurred during data receiving.")
    return None, None
