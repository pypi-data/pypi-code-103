from datetime import datetime
import pytz as pytz


def convert_date_to_timestamp(date, format_datetime='%Y-%m-%d %H:%M:%S'):
    if isinstance(date, str):
        date = datetime.strptime(date, format_datetime)

    if not isinstance(date, datetime):
        raise ValueError('Incorrect data type')

    return int(date.astimezone(pytz.UTC).timestamp())


def get_timestamp_now():
    return int(datetime.now().astimezone(pytz.utc).timestamp())
