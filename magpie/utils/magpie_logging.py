import logging
import os
from logging.config import fileConfig

from magpie.utils.commons import APP_ROOT


def init(log_folder=None, pro_env=False):
    config_file = "/config/logger_config_pro.ini" if pro_env else "/config/logger_config.ini"
    fileConfig(APP_ROOT + config_file, disable_existing_loggers=False)
    if log_folder is not None:
        full_log_folder = log_folder
        os.makedirs(full_log_folder, exist_ok=True)
        root_logger = logging.getLogger()
        file_handler = logging.FileHandler(os.path.join(full_log_folder + "/magpie.log"), "w")
        file_handler.setFormatter(root_logger.handlers[0].formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        core_info_file_handler = logging.FileHandler(os.path.join(full_log_folder + "/core_info.log"), "w")
        core_info_file_handler.setFormatter(root_logger.handlers[0].formatter)
        core_info_file_handler.setLevel(logging.DEBUG)
        core_info_logger = logging.getLogger("core_info")
        core_info_logger.addHandler(core_info_file_handler)
    print("Initializing magpie logger")
    logger = logging.getLogger(__name__)
    logger.info(f"Finish magpie logger initialization.")
    if log_folder is not None:
        logger.info(f"log path: {full_log_folder}/magpie.log")
