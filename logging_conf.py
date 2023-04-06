import logging.config
import os

from config import config

LOGGING_FILE = config.logging.logging_file

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(processName)-10s - %(name)-10s "
            "- %(levelname)s - %(message)-10s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {"format": "%(message)s"},
    },
    "handlers": {
        "logfile": {
            "formatter": "default",
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGGING_FILE,
            "maxBytes": 10485760,
            "backupCount": 5,
        },
        "verbose_output": {
            "formatter": "default",
            "level": config.logging.console_logging_level,
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "telegram_handler": {
            "formatter": "default",
            "level": "ERROR",
            "class": "utils.telegram_bot_logging_handler.TelegramHandler",
            "bot_token": config.logging.bot_token,
            "admin_id": config.admins,
            "bot_name": config.bot_name,
        },
    },
    "loggers": {
        "telegram_bot": {
            "level": "DEBUG",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "logfile",
            "verbose_output",
            "telegram_handler",
        ],
    },
}


def create_logs_folder():
    if not os.path.exists("logs"):
        os.mkdir("logs")


def prepare_logging():
    create_logs_folder()
    logging.config.dictConfig(LOGGING_CONFIG)
