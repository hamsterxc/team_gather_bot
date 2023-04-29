import datetime


DEBUG = 100
INFO = 200
WARN = 300
ERROR = 400
_logging_level_names = {DEBUG: "DEBUG", INFO: "INFO", WARN: "WARN", ERROR: "ERROR"}
_logging_level_values = {"DEBUG": DEBUG, "INFO": INFO, "WARN": WARN, "ERROR": ERROR}

_logging_level = DEBUG


def set_logging_level(logging_level: str):
    global _logging_level
    _logging_level = _logging_level_values.get(logging_level.upper(), INFO)


def error(message: str):
    _log(ERROR, message)


def warn(message: str):
    _log(WARN, message)


def info(message: str):
    _log(INFO, message)


def debug(message: str):
    _log(DEBUG, message)


def _log(level: int, message: str):
    if level >= _logging_level:
        print("{} {:<5} {}".format(
            datetime.datetime.now().isoformat(),
            _logging_level_names.get(level, "INFO"),
            message
        ))
