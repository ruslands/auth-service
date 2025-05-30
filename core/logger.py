import json
import os
import sys

from loguru import logger


__all__ = ("logger",)


# {"message": "My log message", "level": "INFO", "logger": "MyLogger", "my-key": "my-value"} Yandex example


def serialize(record):
    subset = {
        "timestamp": record["time"].timestamp(),  # не обязательно
        "message": record["message"],
        "level": str.replace(str.replace(record["level"].name, "WARNING", "WARN"), "CRITICAL", "FATAL"),
        "logger": record["name"],
    }
    return json.dumps(subset)


def patching(record):
    record["extra"]["serialized"] = serialize(record)


logger.remove()
logger.level("INFO", color="<green>")

if not os.environ.get("ENVIRONMENT", None):
    logger.add(
        sys.stdout,
        colorize=True,
        enqueue=False,
        level="DEBUG",
        format="<green>{time:HH:mm:ss}</green> | {level} | <level>{message}</level>",
    )
else:
    logger = logger.patch(patching)
    if os.environ.get("DEBUG", True):
        logger.add(
            sys.stderr,
            format="{extra[serialized]}",
            colorize=True,
            enqueue=False,
            level="DEBUG",
        )
