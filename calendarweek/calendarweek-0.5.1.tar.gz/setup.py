# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['calendarweek']

package_data = \
{'': ['*']}

extras_require = \
{'django': ['Django>=2.2,<5.0']}

setup_kwargs = {
    'name': 'calendarweek',
    'version': '0.5.1',
    'description': 'Utilities for working with calendar weeks in Python and Django',
    'long_description': "python-calendarweek\n===================\n\npython-calendarweek provides a CalendarWeek dataclass for representing one\nweek in a year, and utility functions to work with it in pure Python or\nDjango.\n\n\nUsage\n-----\n\nThe `CalendarWeek` object\n~~~~~~~~~~~~~~~~~~~~~~~~~\n\nThe main interface is the `CalendarWeek` object. The following example shows its\ninterface.\n\n.. code-block:: python\n\n   from datetime import date\n   from calendarweek import CalendarWeek\n\n   # Create an object for the third week in 2012\n   week = CalendarWeek(year=2012, week=3)\n\n   # Get the current week (or the week for any date)\n   week = CalendarWeek.from_date(date.today())\n\n   # Short-hand for the current week\n   week = CalendarWeek()\n\n   # Get all weeks within a date range\n   start = date(2012, 3, 18)\n   end = date(2012, 4, 19)\n   weeks = CalendarWeek.weeks_within(start, end)\n\n   # Get the last week of a year\n   week = CalendarWeek.get_last_week_of_year(2012)\n\n   # Get the Wednesday of the selected week (or any weekday)\n   day = week[3]\n\n   # Check whether a day is within a week\n   is_contained = day in week\n\n   # Get the week five weeks later\n   week = week + 5\n\n   # Additionally, all comparison operators are implemented\n\n\nDjango utilities\n~~~~~~~~~~~~~~~~\n\nSome utilities for Django are contained in the `calendarweek.django` module:\n\n- `i18n_day_names` — Returns a tuple of localised day names\n- `i18n_day_abbrs` — Returns a tuple of abbreviated, localised day names\n- `i18n_month_names` — Returns a tuple of localised month names\n- `i18n_month_abbrs` — Returns a tuple of abbreviated, localised month names\n- All the above for suffixed with `_choices` to get a list of tuples ready for a model\n  or form field's `choices`\n- `i18n_js` — A view returning the above as JSON ready to be consumed by a frontend\n",
    'author': 'Dominik George',
    'author_email': 'nik@naturalnet.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://edugit.org/AlekSIS/libs/python-calendarweek',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
