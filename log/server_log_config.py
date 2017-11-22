import logging
import logging.handlers
import os


LOG_FOLDER_PATH = os.getcwd()
SERVER_LOF_FILE_PATH = os.path.join(LOG_FOLDER_PATH, 'server.log')
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
server_logger = logging.getLogger('server')
server_handler = logging.handlers.TimedRotatingFileHandler(SERVER_LOF_FILE_PATH, when='d')
server_handler.setFormatter(formatter)
server_logger.addHandler(server_handler)
server_logger.setLevel(logging.INFO)