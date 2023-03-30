import datetime


DEBUG = 100
INFO = 200
WARN = 300
_logging_levels = {DEBUG: "DEBUG", INFO: "INFO", WARN: "WARN"}

logging_level = DEBUG


def warn(message: str):
    _log(WARN, message)


def info(message: str):
    _log(INFO, message)


def debug(message: str):
    _log(DEBUG, message)


def _log(level: int, message: str):
    if level >= logging_level:
        print("{} {:<5} {}".format(
            datetime.datetime.now().isoformat(),
            _logging_levels.get(level, "INFO"),
            message
        ))
