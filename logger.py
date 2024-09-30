import sys

from loguru import logger

logger.remove()

#logger.add(sys.stderr, level="INFO", serialize=False)
logger.add(sys.stderr, level="INFO", colorize=True, format="<green>{time}</green>|<level>{level}</level> - <level>{message}</level>")
