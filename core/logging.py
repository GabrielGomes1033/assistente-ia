import logging
import os

# Configurar logging silencioso para produção
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('assistente.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def debug(msg):
    logger.debug(msg)

def info(msg):
    logger.info(msg)

def error(msg):
    logger.error(msg)
