"""
# Custom Logger
"""

import logging
from typing import Any, cast

from src.utils.constants import OUT_LEVEL

logging.addLevelName(OUT_LEVEL, "OUT")


class PR5Logger(logging.Logger):
    def out(self, message: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(OUT_LEVEL):
            self._log(OUT_LEVEL, message, args, **kwargs)


# Set as default logger class for new loggers
logging.setLoggerClass(PR5Logger)


def setup(name: str = "pr5", logfile: str = "sim.log") -> PR5Logger:
    """Configure and return a PR5Logger instance."""

    logger = logging.getLogger(name)
    logger = cast(PR5Logger, logger)

    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # file handler
        file_handler = logging.FileHandler(logfile, mode="w")
        file_handler.setLevel(logging.DEBUG)

        # formatter
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # attach handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
