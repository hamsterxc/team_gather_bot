import datetime
import zoneinfo

from .parse_exception import ParseException


class TimeParser:
    def __init__(self, now_timestamp: int, timezone: zoneinfo.ZoneInfo):
        self._now_timestamp = now_timestamp
        self._timezone = timezone

    def now(self) -> int:
        return self._now_timestamp

    def parse_datetime(self, input: str) -> int | None:
        if input is None:
            return None

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

        return int(datetime.datetime(year, month, day, hour, minute, second, tzinfo=self._timezone).timestamp())

    def _parse_date(self, input: str, full_input: str) -> list[int]:
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

    def _parse_time(self, input: str, full_input: str) -> list[int]:
        parts = input.split(':')
        if len(parts) == 1:
            return [int(parts[0]), 0, 0]
        elif len(parts) == 2:
            return [int(parts[0]), int(parts[1]), 0]
        elif len(parts) == 3:
            return [int(parts[0]), int(parts[1]), int(parts[2])]
        else:
            raise ParseException(full_input, "datetime")

    def _localize(self, timestamp: int) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(timestamp).astimezone(self._timezone)

    def _now(self) -> datetime.datetime:
        return self._localize(self._now_timestamp)

    def format(self, timestamp: int) -> str:
        return self._localize(timestamp).strftime('%Y-%m-%d %H:%M')
