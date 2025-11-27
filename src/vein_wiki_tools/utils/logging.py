import logging
import logging.config
from functools import cache

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR


@cache
def setup_logging():
    logging.config.dictConfig(LOGGING)


def getLogger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "class": "logging.Formatter",
            "format": "%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s",
            "datefmt": "%Y-%b-%d %H:%M:%S",
        },
    },
    "handlers": {
        "null": {"level": "DEBUG", "class": "logging.NullHandler"},
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "": {
            "level": logging.DEBUG,
            "handlers": ["default"],
            "propagate": False,
        },
    },
}
