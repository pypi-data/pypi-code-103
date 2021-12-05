from datetime import datetime, timedelta, timezone

def count(seq, cond=None):
    """Count the number of items from a sequence matching condition `cond`
    """
    if cond is None:
        cond = lambda x: True

    return sum(1 for x in seq if cond(x))


def single(seq, cond=None):
    """Extract a single item from a sequence matching condition `cond`

    Raises IndexError if there is not exactly one item matching the condition.
    """
    NOMATCH = object()

    result = single_or(seq, NOMATCH, cond)

    if result is NOMATCH:
        raise IndexError("No items found")
    return result


def single_or(seq, default, cond=None):
    """Extract a single item from a sequence matching condition `cond`

    Returns `default` if no item is found.

    Raises IndexError if there is more than one item matching the condition.
    """
    if cond is None:
        cond = lambda x: True

    NOMATCH = object()
    result = NOMATCH

    for x in seq:
        if not cond(x):
            continue
        if result is not NOMATCH:
            raise IndexError("Multiple items found")
        result = x

    if result is NOMATCH:
        result = default
    return result

def int_from_bytes(data, offset, length, byteorder):
    chunk = data[offset : offset+length]
    if len(chunk) != length:
        raise ValueError("Truncated data")

    return int.from_bytes(chunk, byteorder)


def join_nonempty(sep, *values):
    return sep.join((v for v in values if v))


# FILETIME is stored as a large integer that represents the number of
# 100-nanosecond intervals since January 1, 1601 (UTC).
MS_EPOCH = datetime(year=1601, month=1, day=1, tzinfo=timezone.utc)
INT64_MAX = (1<<63)-1
UTCMAX = datetime.max.replace(tzinfo=timezone.utc)

def FILETIME_to_datetime(ts):
    """Converts a FILETIME integer into a datetime object in the UTC timezone.

    If the result cannot be represented in a datetime object, then UTCMAX will
    be returned.
    """
    if ts < 0:
        # Negative timestamps represent relative times
        raise ValueError("ts must be positive")

    dt = timedelta(microseconds=ts/10)
    try:
        return MS_EPOCH + dt
    except OverflowError:
        # AD can return INT64_MAX which is in year 30848, and can't be
        # represented by datetime. We return UTCMAX as a sentinel.
        return UTCMAX

def datetime_to_FILETIME(date):
    """Converts a datetime object to a FILETIME integer.

    date must be an offset-aware datetime (with tzinfo set).

    As a special case, if date == UTCMAX, then INT64_MAX will be returned.
    """
    # While UTCMAX can easily be represented by the range of FILETIME,
    # we want to make this symmetric with FILETIME_to_datetime.
    if date == UTCMAX:
        return INT64_MAX

    dt = date - MS_EPOCH
    sec = dt.days*24*60*60 + dt.seconds
    usec = sec*1000*1000 + dt.microseconds
    return usec * 10

def utcnow():
    return datetime.now(timezone.utc)
