import os
from multiprocessing import Process

import utils.utils as utils_functions
from acquisition_layer.data_sender import DataSender
from configuration import settings
from configuration_managers.client_conifguration_manager import ClientConfigurationManager
from hardware_layer.hardware_data_collector import HardwareDataCollector
from utils.interrupt_handler import InterruptHandler
from utils.utils import setup_logger

# class ClientManager:
#     def __init__(self, command_pipe, result_pipe):
#         self._client_key = None
#         self._server_communicator = ServerCommunicator()
#         self.logger = logging.getLogger("aps")
#         self._data_sender = DataSender(
#             command_pipe,
#             result_pipe,
#         )
#
#     def run(self):
#         # if we already have key then we dont have to register on server
#         self._client_key = ClientKeyHandler.get_assigned_client_key()
#         self.logger.info("CURRENT KEY:{}".format(self._client_key))
#
#         if self._client_key is None:
#             #     or ClientKeyHandler.is_key_valid(
#             #     self._server_communicator, self._client_key) is False:
#             # # getting authorization key for next steps
#             # key = self.register_on_server()
#             # if key is not None:
#             #     self._client_key = key
#             #     ClientKeyHandler.save_client_key(self._client_key)
#             # else:
#             self.logger.error("Could not connect to server during registration.")
#             exit(-1)
#
#         # getting configuration from server
#         self._conf_mgr.get_client_configuration_from_server()
#
#         # start sending data
#         if self._conf_mgr.is_configured_by_server():
#             self._data_sender.set_key(self._client_key)
#             self._data_sender.start_sending_data()
#         else:
#             self.logger.error("General faliure.")
#             exit(-1)
#
#             # def register_on_server(self):
#             #     payload = {
#             #         "monitored_properties": self._conf_mgr['MONITORED_PROPERTIES'],
#             #         "hostname": socket.gethostname(),
#             #         "base_probing_interval": self._conf_mgr['BASE_PROBING_INTERVAL']
#             #     }
#             #
#             #     while True:
#             #         key = self._server_communicator.register_client(data=payload)
#             #         if key is not None:
#             #             ClientKeyHandler.save_client_key(key)
#             #             return key
#             #         else:
#             #             logger.error("Trying again...")
#             #             time.sleep(5)
#
#             # def get_configuration(self):
#             #     while True:
#             #         self._conf_mgr.get_client_configuration_from_server()
#             #         if self._conf_mgr.is_configured_by_server():
#             #             break
#             #         else:
#             #             logger.info("Configuration is not set by server")
#             #
#             #         time.sleep(5)
#
#
# # def load_initial_configuration():
# #     with open(constant_values.BASE_CONFIG_PATH) as configuration_file:
# #         return json.load(configuration_file)

LOGGER = setup_logger()
if __name__ == '__main__':
    try:

        interrupt_handler = InterruptHandler()
        interrupt_handler.register_interrupt_handler()

        r_command_pipe, w_command_pipe = os.pipe()
        r_result_pipe, w_result_pipe = os.pipe()
        hardware_data_collector_process = Process(target=HardwareDataCollector.run, kwargs={
            "command_pipe": r_command_pipe,
            "result_pipe": w_result_pipe
        })
        hardware_data_collector_process.daemon = True
        hardware_data_collector_process.start()
        if settings.DROP_PRIVILEGES:
            utils_functions.drop_privileges(settings.DROP_TO_USERNAME, settings.DROP_TO_GROUP)

        # ClientManager(w_command_pipe, r_result_pipe).run()
        configuration_manager = ClientConfigurationManager()

        # start sending data
        assert configuration_manager.is_configured_by_server(), "Client not configured by server."
        data_sender = DataSender(configuration_manager.key, w_command_pipe, r_result_pipe,)
        data_sender.start_sending_data()

    except Exception:
        LOGGER.exception("FATAL: Could not setup client.")
        exit(-1)
