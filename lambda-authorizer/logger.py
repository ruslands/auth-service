# # Native # #
import sys

# # Installed # #
from loguru import logger

# # Package # #


__all__ = (
    "logger",
)


logger.remove()
logger.level("INFO", color="<green>")
logger.add(sys.stdout, colorize=True, enqueue=False, level="DEBUG",
           format="<green>{time:HH:mm:ss}</green> | {level} | <level>{message}</level>")
