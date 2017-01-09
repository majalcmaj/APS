import json
import logging

from django.views.decorators.csrf import csrf_exempt

from APS.settings import LOGGER_NAME, MESSAGE_DATA_DELIMITER
from acquisition_server.views import utils
from acquisition_server.views.utils import CryptUtils, signed_json_response
from common.libs import ClientManager, MonitoringDataManager, ClientsStateManager
from common.libs.ClientsStateManager import ClientsManagerException

logger = logging.getLogger(LOGGER_NAME)


@csrf_exempt
def monitoring_data(request):
    if request.method == "PUT":
        if request.content_type == "aps/json":
            try:
                digest, data = request.body.split(MESSAGE_DATA_DELIMITER)
                if CryptUtils.validate_signature(data, digest):
                    json_data = json.loads(data.decode("UTF-8"))
                    client = ClientManager.get_client(utils.extract_client_key(json_data))
                    if client is not None:
                        if client.configuration_pending is True:
                            return signed_json_response(status=303, data={
                                "message": "Configuration pending."})  # signed_json_response({"configuration": configuration})
                        else:
                            MonitoringDataManager.process_data(client, json_data['monitored_properties'],
                                                               json_data["timestamp"])
                            return signed_json_response(status=200)
                    else:
                        logger.error("Client with key {} does not exist in database. Address: {}".format(
                            json_data['key'],
                            request.META['REMOTE_ADDR']))
                        return signed_json_response(status=404,
                                                    data={"result": "Client is not registered in database."})
                else:
                    logger.error("Digital signature verification failed.")
                    return signed_json_response(status=401, data={"content": "Digital signature verification failed."})
            except Exception:
                logger.exception("Exception ocurred during sending monitoring data.")
                return signed_json_response(status=400,
                                            data={"content": "Bad request format. Contact administrator for details"})
        else:
            return signed_json_response(status=415, data={"content": "Data sent has be of type 'aps/json' and "
                                                                     "has to be digitally signed"})
    else:
        return signed_json_response(status=405, data={"content": "Methods allowed: PUT"})


@csrf_exempt
def client_configuration(request):
    if request.method == "GET":
        if request.content_type == "aps/json":
            try:
                digest, data = request.body.split(MESSAGE_DATA_DELIMITER)
                if CryptUtils.validate_signature(data, digest):
                    json_data = json.loads(data.decode("UTF-8"))
                    client = ClientManager.get_client_anystate(
                        utils.extract_client_key(json_data))
                    if client is not None:
                        if client.configuration_pending or client.is_configured:
                            configuration = utils.return_client_configuration(client)
                            return signed_json_response(status=200, data=configuration)
                        else:
                            return signed_json_response(status=202)
                    else:
                        logger.error("Client with key {} does not exist in database. Address: {}".format(
                            json_data['key'],
                            request.META['REMOTE_ADDR']))
                        return signed_json_response(status=404,
                                                    data={"result": "Client is not registered in database."})
                else:
                    logger.error("Digital signature verification failed.")
                    return signed_json_response(status=401, data={"content": "Digital signature verification failed."})

            except Exception:
                logger.exception("Exception ocurred during client configuration request.")
                return signed_json_response(status=400,
                                            data={"content": "Bad request format. Contact administrator for details"})
        else:
            return signed_json_response(status=415, data={"content": "Data sent must be of type 'aps/json'"})
    else:
        return signed_json_response(status=405, data={"content": "Methods allowed: GET"})


@csrf_exempt
def client_identity(request):
    if request.method == "POST":
        if request.content_type == "aps/json":
            try:
                digest, data = request.body.split(MESSAGE_DATA_DELIMITER)
                if CryptUtils.validate_signature(data, digest):
                    json_data = json.loads(data.decode("UTF-8"))
                    client = ClientManager.get_client_anystate(
                        utils.extract_client_key(json_data))
                    if client is not None:
                        return signed_json_response(status=200)
                    else:
                        return signed_json_response(status=404)
                else:
                    logger.error("Digital signature verification failed.")
                    return signed_json_response(status=401, data={"content": "Digital signature verification failed."})
            except Exception:
                logger.exception("Exception ocurred during checking client id.")
                return signed_json_response(status=400,
                                            data={"content": "Bad request format. Contact administrator for details"})
        else:
            return signed_json_response(status=415, data={"content": "Data sent must be of type 'aps/json'"})
    elif request.method == "GET":
        if request.content_type == "aps/json":
            try:
                digest, data = request.body.split(MESSAGE_DATA_DELIMITER)
                if CryptUtils.validate_signature(data, digest):
                    json_data = json.loads(data.decode("UTF-8"))
                    key = ClientsStateManager.register_new_pending_client(json_data['hostname'],
                                                                          request.META['REMOTE_ADDR'],
                                                                          json_data['monitored_properties'],
                                                                          json_data['base_probing_interval'],
                                                                          )
                    return signed_json_response({"key": key})
                else:
                    logger.error("Digital signature verification failed.")
                    return signed_json_response(status=401, data={"content": "Digital signature verification failed."})
            except ClientsManagerException as e:
                logger.exception("Exception ocurred during client registration request.")
                return signed_json_response(status=409, data={"message": e.message})
            except Exception as e:
                logger.exception("Exception occured during client registration request.")
                return signed_json_response(status=400,
                                            data={"content": "Bad request format. Contact administrator for details"})
        else:
            return signed_json_response(status=415, data={"content": "Data sent must be of type 'aps/json'"})
    else:
        return signed_json_response(status=405, data={"content": "Methods allowed: HEAD, POST"})
