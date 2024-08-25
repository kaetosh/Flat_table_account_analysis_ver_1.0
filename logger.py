from loguru import logger

log_path = "logs.log"
logger.add(log_path, level="INFO", mode='w')

