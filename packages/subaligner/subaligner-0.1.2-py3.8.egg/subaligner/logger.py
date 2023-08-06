import logging
from typing import Dict
from absl import logging as absl_logging
from .singleton import Singleton
absl_logging._warn_preinit_stderr = 0


class Logger(Singleton):
    """Common logging."""

    VERBOSE = True
    QUIET = False

    def __init__(self, output_log: str = "output.log"):
        self.__loggers: Dict[str, logging.Logger] = {}
        self.__output_log = output_log

    def get_logger(self, name: str) -> logging.Logger:

        if self.__loggers.get(name) is not None:
            return self.__loggers.get(name)  # type: ignore
        else:
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
            if Logger.VERBOSE:
                logger.setLevel(logging.DEBUG)
            if Logger.QUIET:
                logger.setLevel(logging.ERROR)
            formatter = logging.Formatter(
                "%(name)s - %(levelname)s - %(threadName)-9s - %(message)s"
            )

            file_handler = logging.FileHandler(self.__output_log, "w+")
            logger.propagate = False
            file_handler.setFormatter(formatter)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            if not logger.handlers:
                logger.addHandler(file_handler)
                logger.addHandler(console_handler)

            self.__loggers[name] = logger
            return logger
