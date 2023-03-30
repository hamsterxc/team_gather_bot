import datetime
from .parse_exception import ParseException
import pytz


TYPE_SCHEDULE = 0
TYPE_START = 1
TYPE_STOP = 2
TYPE_CANCEL = 3


class AbstractCommand:
    action: int
    chat_id: str
    message_id: int

    def __init__(self, action: int, chat_id: str, message_id: int):
        self.action = action
        self.chat_id = chat_id
        self.message_id = message_id


class ScheduleCommand(AbstractCommand):
    _DEFAULT_MAX = 6

    start: int
    end: int
    max: int
    what: str
    where: str
    when: str

    def __init__(self, chat_id: str, message_id: int, start: str, end: str, max: str, what: str, where: str, when: str):
        super().__init__(TYPE_SCHEDULE, chat_id, message_id)
        self.start = self._parse_datetime(start)
        self.end = self._parse_datetime(end)
        self.max = int(max) if max is not None else self._DEFAULT_MAX
        self.what = what
        self.where = where
        self.when = when

    def _parse_datetime(self, input: str) -> int:
        if input is None:
            return int(datetime.datetime.now().timestamp())

        parts = input.split('T')
        if len(parts) == 1:
            now = datetime.datetime.now()
            date = [now.year, now.month, now.day]
            time = self._parse_time(input, input)
        elif len(parts) == 2:
            date = self._parse_date(parts[0], input)
            time = self._parse_time(parts[1], input)
        else:
            raise ParseException(input, "datetime")

        return int(datetime.datetime(date[0], date[1], date[2], time[0], time[1], time[2]).timestamp())

    def _parse_date(self, input: str, full_input: str):
        parts = input.split('-')
        if len(parts) == 1:
            now = datetime.datetime.now()
            return [now.year, now.month, int(parts[0])]
        elif len(parts) == 2:
            now = datetime.datetime.now()
            return [now.year, int(parts[0]), int(parts[1])]
        elif len(parts) == 3:
            return [int(parts[0]), int(parts[1]), int(parts[2])]
        else:
            raise ParseException(full_input, "datetime")

    def _parse_time(self, input: str, full_input: str):
        parts = input.split(':')
        if len(parts) == 1:
            return [int(parts[0]), 0, 0]
        elif len(parts) == 2:
            return [int(parts[0]), int(parts[1]), 0]
        elif len(parts) == 3:
            return [int(parts[0]), int(parts[1]), int(parts[2])]
        else:
            raise ParseException(full_input, "datetime")


class StartCommand(AbstractCommand):
    def __init__(self, chat_id: str, message_id: int):
        super().__init__(TYPE_START, chat_id, message_id)


class StopCommand(AbstractCommand):
    def __init__(self, chat_id: str, message_id: int):
        super().__init__(TYPE_STOP, chat_id, message_id)


class CancelCommand(AbstractCommand):
    def __init__(self, chat_id: str, message_id: int):
        super().__init__(TYPE_CANCEL, chat_id, message_id)
