"""Messages to output for the user."""

import datetime as dt

MSG_DATETIME_FORMAT = "%m/%d/%y %H:%M:%S"
MSG_DAYS_LEN = 3
MSG_DESCR_LEN = 40
MSG_ITER_HALF_LEN = 5
MSG_SEPARATOR = " | "
from eagers.basic.datetime_ext import timedelta_split


def success(text):
    return f"SUCCESS: {text}"


def sim_loop_start(proj_name, t_sim_start):
    """Create string for logging start of simulation.
    
    Positional arguments:
    t_sim_start - (datetime) Time simulation started.
    """
    t_now = dt.datetime.now()
    now = s_datetime(t_now)
    proj_descr = s_descr(proj_name)
    iter_ = f"{'START':*^{2*MSG_ITER_HALF_LEN + 1}}"
    tot_elaps = s_duration(t_now - t_sim_start)
    return MSG_SEPARATOR.join([now, proj_descr, iter_, tot_elaps])


def sim_loop_iteration(proj_name, t_sim_start, i, n):
    """Create string for logging a single simulation loop iteration.

    Positional arguments:
    proj_name - (str) Project name.
    t_sim_start - (datetime) Time simulation started.
    i - (int) Iteration count (1 to n).
    n - (int) Total number of iterations to be performed.
    """
    t_now = dt.datetime.now()
    now = s_datetime(t_now)  # 17 c.
    proj_descr = s_descr(proj_name)  # 40 c.
    iter_ = s_iter(i, n)  # 11 c.
    tot_elaps = s_duration(t_now - t_sim_start)  # 13 c.
    remaining = s_duration((t_now - t_sim_start) / i * (n - i))  # 13 c.
    # Default shell width: 120 characters.
    # Total length: 17 + 40 + 11 + 13 + 4 + 13 + (3 * 4) = 110 c.
    return MSG_SEPARATOR.join([now, proj_descr, iter_, tot_elaps, f"rem {remaining}"])


def s_datetime(d):
    return d.strftime(MSG_DATETIME_FORMAT)


def s_descr(d):
    return f"{truncate(d, MSG_DESCR_LEN):<{MSG_DESCR_LEN}}"


def s_iter(i, n):
    return f"{i:>{MSG_ITER_HALF_LEN}}/{n:<{MSG_ITER_HALF_LEN}}"


def s_duration(d, show_days=True):
    """String representing given time duration.

    Positional arguments:
    d - (timedelta) Time duration.

    Keyword arguments:
    show_days - (bool) (Default: True) Whether to show number of days.
    """
    d_day, d_hr, d_min, d_sec = timedelta_split(d)
    if not show_days:
        d_hr += 24 * d_day
        return f"{d_hr:02}:{d_min:02}:{d_sec:02.0f}"
    return f"{d_day:>{MSG_DAYS_LEN}}d {d_hr:02}:{d_min:02}:{d_sec:02.0f}"

def truncate(text, max_len, tail=0, rep='...', *, spill_to_newlines=False):
    """Truncate the input string, keeping a number of characters at the end.

    Positional arguments:
    text -- String to be shortened.
    max_len -- Maximum length of string.

    Keyword arguments:
    tail -- Number of characters to keep at the end. Default: 0
    rep -- String to replace removed text. Default: "..."
    """
    assert (
        max_len > len(rep) + tail
    ), "Character limit does not allow enough room for shortening."
    if len(text) <= max_len:
        return text
    elif spill_to_newlines:
        return '\n'.join(
            text[i:i+max_len] for i in range(0, len(text), max_len))
    else:
        assert tail > -1, "tail must be non-negative."
        cutoff = max_len - tail - len(rep)
        tail_str = '' if tail == 0 else text[-tail:]
        return text[:cutoff] + rep + tail_str