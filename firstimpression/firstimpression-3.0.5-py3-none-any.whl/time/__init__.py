import datetime


def parse_string_to_date(element: str, format: str):
    return datetime.datetime.strptime(element, format)


def parse_timestamp_to_date(timestamp: float):
    return datetime.datetime.fromtimestamp(timestamp)


def parse_date_to_string(date_object: datetime.datetime, format: str):
    return datetime.datetime.strftime(date_object, format)


def parse_string_time_to_minutes(element: str):
    [hours, minutes, seconds] = element.split(':')

    minutes = int(minutes)

    if int(seconds) > 30:
        minutes += 1

    minutes += int(hours) * 60

    return minutes


def parse_string_to_string(element: str, format: str, new_format: str):
    if not element == '':
        return parse_date_to_string(parse_string_to_date(element, format), new_format)
    else:
        return ''
