import logging
import logging.handlers
import os

LOG_FOLDER_PATH = os.getcwd()
CLIENT_LOG_FILE_PATH = os.path.join(LOG_FOLDER_PATH, 'client.log')

client_logger = logging.getLogger('client')
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
client_handler = logging.FileHandler(CLIENT_LOG_FILE_PATH, encoding='utf-8')
client_handler.setLevel(logging.INFO)
client_handler.setFormatter(formatter)
client_logger.addHandler(client_handler)
client_logger.setLevel(logging.INFO)