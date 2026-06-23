from logging import DEBUG, Formatter, StreamHandler, getLogger
from sys import stdout

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def console_handler():
    """Create a StreamHandler that logs to stdout with LOG_FORMAT."""
    tmp_handler = StreamHandler(stdout)
    tmp_handler.setFormatter(Formatter(LOG_FORMAT))
    return tmp_handler


def log_arbiter(logger_name: str = ""):
    """Create a DEBUG-level stdout logger that does not propagate."""
    tmp_logger = getLogger(logger_name)
    tmp_logger.setLevel(DEBUG)
    tmp_logger.addHandler(console_handler())
    tmp_logger.propagate = False
    return tmp_logger
