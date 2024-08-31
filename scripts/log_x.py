from logging import DEBUG, INFO, Formatter, StreamHandler, getLogger
from sys import stdout

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def console_handler():
    """
    Creates a StreamHandler that logs to stdout with a custom LOG_FORMAT format.

    Returns:
        StreamHandler: The created handler.
    """
    tmp_handler = StreamHandler(stdout)
    tmp_handler.setFormatter(Formatter(LOG_FORMAT))
    return tmp_handler


def log_arbiter(logger_name: str = ""):
    """
    Creates a logger with the given name that logs to stdout with the custom LOG_FORMAT format.

    The logger has a level of DEBUG and does not propagate to its parent.

    Args:
        logger_name (str): The name of the logger to create.

    Returns:
        Logger: The created logger.
    """

    tmp_logger = getLogger(logger_name)
    tmp_logger.setLevel(DEBUG)
    tmp_logger.addHandler(console_handler())
    tmp_logger.propagate = False
    return tmp_logger
