import logging

from app.utils.constants import APP_NAME

logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.ERROR)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)