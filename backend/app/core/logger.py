import logging
import sys
from app.core.config import settings

def setup_logging():
    log_level = logging.INFO if settings.app_env == "production" else logging.DEBUG
    
    # Configuración del formato para ser fácil de parsear en VPS/Cloud
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Limpiar handlers previos si existen
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(handler)
    
    # Silenciar librerías ruidosas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.WARNING)
    
    return logging.getLogger("maspizzas")

logger = setup_logging()
