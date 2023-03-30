from .parse_exception import ParseException
import datetime
import pytz


class TimeParser:
    timezone: datetime.tzinfo

    def __init__(self, timezone: str):
        self.timezone = pytz.timezone(timezone)

    def parse_datetime(self, input: str) -> int:
        if input is None:
            return int(self._now().timestamp())

        parts = input.split('T')
        if len(parts) == 1:
            now = self._now()
            year, month, day = [now.year, now.month, now.day]
            hour, minute, second = self._parse_time(input, input)
        elif len(parts) == 2:
            year, month, day = self._parse_date(parts[0], input)
            hour, minute, second = self._parse_time(parts[1], input)
        else:
            raise ParseException(input, "datetime")

        return int(datetime.datetime(year, month, day, hour, minute, second).timestamp())

    def _parse_date(self, input: str, full_input: str) -> list:
        parts = input.split('-')
        if len(parts) == 1:
            now = self._now()
            return [now.year, now.month, int(parts[0])]
        elif len(parts) == 2:
            now = self._now()
            return [now.year, int(parts[0]), int(parts[1])]
        elif len(parts) == 3:
            return [int(parts[0]), int(parts[1]), int(parts[2])]
        else:
            raise ParseException(full_input, "datetime")

    def _parse_time(self, input: str, full_input: str) -> list:
        parts = input.split(':')
        if len(parts) == 1:
            return [int(parts[0]), 0, 0]
        elif len(parts) == 2:
            return [int(parts[0]), int(parts[1]), 0]
        elif len(parts) == 3:
            return [int(parts[0]), int(parts[1]), int(parts[2])]
        else:
            raise ParseException(full_input, "datetime")

    def _now(self):
        return datetime.datetime.now(self.timezone)
