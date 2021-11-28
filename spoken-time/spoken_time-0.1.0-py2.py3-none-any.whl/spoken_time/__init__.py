from datetime import datetime
from num2words import num2words
import gettext as gettext_module, locale, os


__all__ = ('spoken_time', 'absolute_spoken_date', 'relative_spoken_date')
__version__ = '0.1.0'

# Reset locale for day & month names
locale.setlocale( locale.LC_ALL, '')

# Load translations for current locale
_language, _encoding = locale.getlocale()
_translation = gettext_module.translation( 'spoken_time',
    languages = [_language], fallback=True,
    localedir = os.path.join( os.path.dirname(__file__), 'locale'))
_ = _translation.gettext
ngettext = _translation.ngettext
del _encoding, _translation


def spoken_minute( m):
    return ngettext( 'one minute',
        '{minutes} minutes', m).format( minutes=m)


def spoken_time( t=None, hours=None, am_pm=True, colloquial=True):
    """ Localize the time of day.
        :param t: timestamp (datetime.time or datetime.datetime), defaults to current time.
        :param hours: 12 or 24, defaults to localization specific value.
        :param am_pm: Include time of day? (Default: yes)
        :param colloquial: Try to sound more natural e.g. 'quarter past noon'.
    """
    
    if not t: t = datetime.now()
    try:
        hours = hours or int( _('{hours_in_clock}'))
    except ValueError:
        hours = 12
    assert hours == 12 or hours == 24
    am_pm = time_of_day( t) if am_pm and hours == 12 else ''
    
    num_hour = (t.hour + hours - 1) % hours + 1
    minutes = spoken_minute( t.minute)
    next_num_hour = (t.hour + hours) % hours + 1
    to_minutes = spoken_minute( 60 - t.minute)

    hour = ngettext( "one o'clock",
        "{hour} o'clock", num_hour).format( hour=num_hour)
    next_hour = ngettext( "one o'clock",
        "{hour} o'clock", next_num_hour).format( hour=next_num_hour)
    
    # Ensure correct pronounciation after stripping blanks
    num_hour = num2words( num_hour, lang=_language)
    next_num_hour = num2words( next_num_hour, lang=_language)

    if colloquial:
        if t.hour == 11:
            next_hour = _('noon')
            am_pm = ''
        elif t.hour == 12:
            hour = _('noon')
            am_pm = ''
        elif t.hour == 23:
            next_hour = _('midnight')
            am_pm = ''
        elif t.hour ==  0:
            hour = _('midnight')
            am_pm = ''
        
    if t.minute == 0: 
        text = _("{hour} {am_pm}")
    elif t.minute == 15: 
        text = _("quarter past {num_hour} {am_pm}")
    elif t.minute == 30: 
        text = _("half past {num_hour} {am_pm}")
    elif t.minute == 45:
        text = _("quarter to {next_num_hour} {am_pm}")
    elif t.minute in (40, 50) or t.minute >= 50:
        text = _("{to_minutes} to {next_num_hour} {am_pm}")
    else: text = _("{minutes} past {hour} {am_pm}")

    return text.format( **locals()).strip()


def time_of_day( t=None):
    "Localize the part of the day like 'afternoon', 'evening' etc."

    if not t: t = datetime.now()
    if  0 <= t.hour <=  4: return _( 'at night')
    if  4  < t.hour <=  9: return _( 'in the morning')
    if  9  < t.hour <= 11: return _( 'before noon')
    if 11  < t.hour <= 12: return _( 'around noon')
    if 12  < t.hour <= 17: return _( 'in the afternoon')
    if 17  < t.hour <= 21: return _( 'in the evening')
    if 21  < t.hour <= 23: return _( 'at night')
    return '' # Noon or midnight


def absolute_spoken_date( dt=None, format=None, cardinal_day=False):
    
    """ Describe a date in human-understandable words.
        :param dt: date (or datetime), defaults to current day.
        :param format: Format string with variables {weekday}, {day}, {month} and {year}.
        :param cardinal_day: Use an ordinal or cardinal day number.
        :return: locaalised formatted string.
    """

    if dt is None: dt = datetime.now()
    if type( dt) is datetime: dt = dt.date()
    format = format or _("{weekday}, the {day} of {month} {year}")
    
    weekday = locale.nl_langinfo( locale.DAY_1 + (dt.weekday() + 1) % 7)
    month = locale.nl_langinfo( locale.MON_1 + dt.month - 1)
    day = num2words( dt.day, lang=_language,
        to='cardinal' if cardinal_day else 'ordinal')
    year = dt.year
    
    return format.format( **locals())


def relative_spoken_date( dt=None, preposition=''):
    "Describe the time span to a date in human-understandable words"

    if dt is None: dt = datetime.now()
    if type( dt) is datetime: dt = dt.date()
    delta = dt - datetime.now().date()

    if delta.days == -2:
        return _("day before yesterday").format( days=-delta.days)
    if delta.days == -1: return _("yesterday")
    if delta.days == 0: return _("today")
    if delta.days == 1: return _("tomorrow")
    if delta.days == 2: return _("the day after tomorrow")

    weekday = locale.nl_langinfo( locale.DAY_1 + (dt.weekday() + 1) % 7)
    
    if -7 <= delta.days < 0:
        return _("{preposition} last {weekday}").format(
            preposition=preposition, weekday=weekday).strip()
    if 0 < delta.days <= 7:
        return _("{preposition} next {weekday}").format(
            preposition=preposition, weekday=weekday).strip()
