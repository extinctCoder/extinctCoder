from logging import DEBUG, INFO, Formatter, StreamHandler, getLogger
from sys import stdout

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def console_handler():
    tmp_handler = StreamHandler(stdout)
    tmp_handler.setFormatter(Formatter(LOG_FORMAT))
    return tmp_handler


def log_arbiter(logger_name: str = ""):
    tmp_logger = getLogger(logger_name)
    tmp_logger.setLevel(DEBUG)
    tmp_logger.addHandler(console_handler())
    tmp_logger.propagate = False
    return tmp_logger
