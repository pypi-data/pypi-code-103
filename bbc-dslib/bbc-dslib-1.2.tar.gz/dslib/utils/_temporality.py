from datetime import date, timedelta, datetime

from dateutil import tz


def midpoint_date(first_date: date, second_date: date, mid_at: float = 0.5) -> date:
    """
    Returns the midpoint date between two dates
    :param first_date: first date in chronological order
    :param second_date: second date in chronological order
    :param mid_at: change the position of the mid date (e.g. put it at two third rather than at the exact midpoint)
    :return: midpoint date
    """
    return first_date + (second_date - first_date) * mid_at


def date_range(start_date: date, end_date: date):
    """
    Returns a generator of all ordered dates between `start_date` and `end_date`.
    :param start_date: first date of the `date_range` generator
    :param end_date: last date of the `date_range` generator
    :return: generator of dates
    """
    return (start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1))


def change_timezone(timestamp: datetime, timezone_name: str):
    """
    Takes a timestamp and changes its timezone to a provided timezone_name. If the provided timestamp is not timezone-
    aware, it is considered UTC.
    :param timestamp: timezone-aware or not (in which case it is considered UTC)
    :param timezone_name: name of the timezone to change to (e.g. "America/Sao_Paulo")
    :return: timezone-aware timestamp
    """
    timezone = tz.gettz(timezone_name)
    if timezone is not None:
        return timestamp.astimezone(timezone)
    else:
        raise ValueError(f'Could not find timezone with name: {timezone_name}')


def force_timezone_onto_timestamp(timestamp: datetime, timezone_name: str):
    """
    Takes a timestamp (timezone-aware or not) and forces a specific timezone to it. For instance, applying this function
    to a "1pm in UTC" timestamp with a "Europe/Paris" timezone_name would result in a "1pm, CET" timestamp.
    :param timestamp: timestamp (timezone-aware or not)
    :param timezone_name: name of the timezone to force onto the timestamp (e.g. "America/Sao_Paulo")
    :return: timezone-aware timestamp
    """
    timezone = tz.gettz(timezone_name)
    if timezone is not None:
        return timestamp.replace(tzinfo=timezone)
    else:
        raise ValueError(f'Could not find timezone with name: {timezone_name}')
