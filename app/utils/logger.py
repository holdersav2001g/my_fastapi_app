import logging
from app.config import Settings

def setup_logger(settings: Settings):
    logger = logging.getLogger("my_fastapi_app")
    logger.setLevel(settings.LOG_LEVEL)
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger