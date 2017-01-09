LAST_CONFIG_PROMPT = "Client has already been conifgured by server. Restore conifguration[Y/n]:"
LAST_CONFIG_PATH = "configuration/last_configuration.json"
BASE_CONFIG_PATH = "configuration/base_config.json"

CLIENT_KEY_FILE = "configuration/client_key"

LOGGING_BASE_FILE = "aps.log"
LOGGING_TEMP_FILE = "tmp.log"

DIGITAL_SIGNATURE_SECRET = b"894d37da41fb91344a4d1e87412986ad1db183a677a20be2076a7623c24a32a7"
MESSAGE_DATA_DELIMITER = b"<<DATA>>"

DROP_PRIVILEGES = False
DROP_TO_USERNAME = "mc"
DROP_TO_GROUP = "mc"

SERVER_IP = "127.0.0.1"
SERVER_PORT = "13000"
SERVER_URL = "http://{0}:{1}/aps_client/".format(SERVER_IP,SERVER_PORT)
MONITORING_DATA_URL = SERVER_URL + "monitoring_data"
CLIENT_IDENTITY_URL = SERVER_URL + "client_identity"
CLIENT_CONFIGURATION_URL= SERVER_URL + "client_configuration"
CUSTOM_APP_HEADER = {"content-type": "aps/json"}


MONITORED_PROPERTIES = {
    "cpu_usage": "%",
    "ram_usage": "MB",
    "free_disk_space": "MB"
}

LUMEL_MONITORING = False
LUMEL_IP = "localhost"
LUMEL_PORT = "8300"

BASE_PROBING_INTERVAL = 2

LOGGER_NAME = "aps"
LOGGING_LEVEL = "DEBUG"
LOG_FORMAT = '[%(asctime)s %(levelname)s \t]: %(message)s'

