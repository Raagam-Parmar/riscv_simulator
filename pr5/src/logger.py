import logging

from utils.constants import OUT_LEVEL

logging.addLevelName(OUT_LEVEL, "OUT")

# ### down
# def log_out(self, message: str, *args, **kwargs):
#     if self.isEnabledFor(OUT_LEVEL):
#         self._log(OUT_LEVEL, message, args, **kwargs)

# logging.Logger.out = log_out
# ### up

class PR5Logger(logging.Logger):
    def out(self, message: str, *args, **kwargs) -> None:
        if self.isEnabledFor(OUT_LEVEL):
            self._log(OUT_LEVEL, message, args, **kwargs)

# Set as default logger class for new loggers
logging.setLoggerClass(PR5Logger)


def setup() -> PR5Logger:
    logger = logging.getLogger("pr5")
    logger.setLevel(logging.DEBUG)
    
    # logging to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    # console_handler.setLevel(logging.DEBUG)
    
    # logging to a file
    file_handler = logging.FileHandler("sim.log", mode='w')
    file_handler.setLevel(logging.DEBUG)
    
    # log format
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
