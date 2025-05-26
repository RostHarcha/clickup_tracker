from contextlib import suppress
from datetime import datetime, time, timedelta


def stringify_timedelta(td: timedelta) -> str:
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f'{hours:02}:{minutes:02}:{seconds:02}'


def _parse_date(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        with suppress(ValueError):
            return datetime.strptime(value, '%d.%m.%y')  # noqa: DTZ007
        now = datetime.now()  # noqa: DTZ005
        with suppress(ValueError):
            return datetime.strptime(value, '%d.%m').replace(year=now.year)  # noqa: DTZ007
        with suppress(ValueError):
            return datetime.strptime(value, '%d').replace(  # noqa: DTZ007
                year=now.year, month=now.month
            )
    msg = 'Неверный формат даты.'
    raise ValueError(msg)


def parse_date(value: str | datetime, min: bool = False, max: bool = False):
    value = _parse_date(value)
    min_or_max = time.min if min else time.max if max else None
    if min_or_max is not None:
        value = value.replace(
            hour=min_or_max.hour,
            minute=min_or_max.minute,
            second=min_or_max.second,
            microsecond=min_or_max.microsecond,
        )
    return value


def parse_dates(text: str):
    from_date, to_date = text.split('-')
    return (
        datetime.strptime(from_date, '%d.%m.%y').replace(  # noqa: DTZ007
            hour=time.min.hour,
            minute=time.min.minute,
            second=time.min.second,
        ),
        datetime.strptime(to_date, '%d.%m.%y').replace(  # noqa: DTZ007
            hour=time.max.hour,
            minute=time.max.minute,
            second=time.max.second,
            microsecond=time.max.microsecond,
        ),
    )
