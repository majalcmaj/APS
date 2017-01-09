from multiprocessing import Process, Pipe

import utils.utils as utils_functions
from acquisition_layer.data_sender import DataSender
from configuration import settings
from configuration_managers.client_conifguration_manager import ClientConfigurationManager
from hardware_layer.hardware_data_collector import HardwareDataCollector
from utils.interrupt_handler import InterruptHandler
from utils.utils import setup_logger

LOGGER = setup_logger()


def setup():
    try:
        interrupt_handler = InterruptHandler()
        interrupt_handler.register_interrupt_handler()

        parent_pipe, child_pipe = Pipe()
        hdc = HardwareDataCollector(child_pipe)
        hardware_data_collector_process = Process(target=lambda: hdc.run())
        hardware_data_collector_process.daemon = True
        hardware_data_collector_process.start()
        if settings.DROP_PRIVILEGES:
            utils_functions.drop_privileges(settings.DROP_TO_USERNAME, settings.DROP_TO_GROUP)

        configuration_manager = ClientConfigurationManager(hdc.available_plugins)
        return DataSender(configuration_manager, parent_pipe)
    except Exception as e:
        LOGGER.error("FATAL: Could not setup client.")
        raise e


if __name__ == '__main__':
    try:
        data_sender = setup()
        data_sender.start_sending_data()
    except Exception:
        LOGGER.exception("FATAL: Client has stopped working due to an exception.")
        exit(-1)
