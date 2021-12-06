"""main

The main module for handling initial scheduling, flask app initialisation and flask routes.

If run as a python module, it will populate the template initially using data from the
nation CSV file and schedule two initial updates for news and covid data.

If run using `flask run` it will not initially load any data or schedule any updates.

It uses the following internal functions:
 * generate_update_content(update)
    -> Generate a summary string that summarises the data of update
 * handle_add_update(args)
    -> Handles an add_update request, scheduling either a covid or news update
 * handle_remove_update(args)
    -> Handles an remove_update request, removing an update by the given name
 * handle_remove_news_article(args):
    -> This function handles a remove_news_article request,
        removing a news update with the given title
 * index()
    -> Main flask route, handles all requests and renders out the template.
"""

import time

from os import path
from datetime import datetime, timedelta
from typing import Dict, List

from flask import Flask, render_template, request

from . import covid_data_handler, covid_news_handler, scheduler

from .config import get_config
from .logger import log_debug, log_error

# Create our flask app
app = Flask(
    __name__,
    template_folder=path.join(get_config('resource_path'), 'templates'),
    static_folder=path.join(get_config('static_path'))
)

def generate_update_content(updates: List[Dict]) -> str:
    """
    This function converts an update object to a content summary string

    Parameters
    ----------
    updates : dictionary[]
        An array of update objects to use data values from
        Each update object should contain the following keys
            - repeating : bool
            - type : str
            - time : float
ß
    Returns
    -------
    str
        A summary of the updates' data.
        e.g. A news update occuring at 10:40 every day
    """
    update_string = ""
    for update in updates:
        if update["repeating"]:
            update_string += (
                f"{update['type']} update occuring at "
                f"{time.strftime('%H:%M:%S', time.localtime(update['time']))} every day.\t"
            )
        else:
            update_string += (
                f"{update['type']} update occuring at "
                f"{time.strftime('%H:%M:%S', time.localtime(update['time']))} on "
                f"{time.strftime('%d-%m-%Y', time.localtime(update['time']))}.\t"
            )

    return update_string


def handle_add_update(args) -> None:
    """
    This function handles an add_update request, scheduling either a covid or news update

    Parameters
    ----------
    args : MultiDict[str, str]
        This contains the arguments provided by the flask request object
        It should contain:
         - alarm : string
            The hour:minute time of the update
         - two : string
            The name of the update
         - repeat : any
            If repeat is not None, the update will repeat
         - covid-data : any
            If not None, cause a covid data update
         - news
            If not None, cause a news update
    """

    alarm = args.get('alarm')
    name = args.get('two')

    repeat = args.get('repeat') is not None
    covid_data = args.get('covid-data') is not None
    news = args.get('news') is not None

    # Convert Hour Minute to absolute timestamp
    new_time = 0

    if alarm != "":
        wanted_time = datetime.strptime(alarm, '%H:%M').time()
        today = datetime.today()
        date = today.date()
        current_time = today.time()

        if wanted_time < current_time:
            date += timedelta(days=1)

        new_time = datetime.combine(
            date,
            wanted_time
        ).timestamp()

    if covid_data:
        covid_data_handler.schedule_covid_updates(new_time, name, repeat=repeat)

    if news:
        covid_news_handler.schedule_news_updates(new_time, name, repeat=repeat)


def handle_remove_update(args) -> None:
    """
    This function handles a remove_update request, removing an update by the given name

    Parameters
    ----------
    args : MultiDict[str, str]
        This contains the arguments provided by the flask request object
        It should contain:
         - alarm_item : str
            The name of the update to be removed.
    """

    name = args.get('alarm_item')

    scheduler.cancel_task_by_name(name)

def handle_remove_news_article(args) -> None:
    """
    This function handles a remove_news_article request,
    removing a news update with the given title

    Parameters
    ----------
    args : MultiDict[str, str]
        This contains the arguments provided by the flask request object
        It should contain:
         - notif : str
            The title of the article to be removed.
    """
    article_title = args.get('notif')

    covid_news_handler.remove_article_by_title(article_title)

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index() -> str:
    """
    This is the single flask route used in this project.
    It handles all requests and renders out the template.

    It takes no parameters but interally uses
    flask.request
    to receive request data (such as query arguments)

    Returns
    -------
    str
        The rendered HTML template
    """

    # Handle parameters
    try:
        if request.args.get('alarm') is not None:
            handle_add_update(request.args)
        elif request.args.get('alarm_item') is not None:
            handle_remove_update(request.args)
        elif request.args.get('notif') is not None:
            handle_remove_news_article(request.args)
    except Exception as err:
        log_error("Unexpected error", err)

    scheduler.run_scheduler()

    config = get_config()
    template_config = get_config('template')

    # Covid and news updates are scheduled separately
    # As such we need to combine any updates with the same name
    scheduled_updates = {}
    for update in scheduler.scheduled_updates:
        name = update['name']
        if name in scheduled_updates:
            update_object = scheduled_updates[name]
            update_object["updates"].append(update)
        else:
            update_object = {
                "name": name,
                "updates": [update]
            }
            scheduled_updates[name] = update_object

    updates = []
    for name, update_object in scheduled_updates.items():
        update_data = {
            "title": name,
            "content": generate_update_content(update_object["updates"])
        }

        updates.append(update_data)

    return render_template('index.html',
        title = template_config['title'],
        favicon = f"/static/images/{template_config['favicon']}",
        image = template_config['logo'],
        location = config['location'],
        nation_location = config['nation_location'],

        local_7day_infections = str(covid_data_handler.covid_data['localCases7Days']),
        national_7day_infections = str(covid_data_handler.covid_data['nationalCases7Days']),
        hospital_cases = (
            f"{str(covid_data_handler.covid_data['nationalHospitalCases'])} hospital cases"
        ),
        deaths_total = f"{str(covid_data_handler.covid_data['nationalCumDeaths'])} deaths",

        updates=updates,
        # Limit the number of news articles to 6
        news_articles = covid_news_handler.news_articles[:5]
    )

def main() -> None:
    """
    This is the first function to run in the program.
    It loads the initial CSV data and then schedules two updates;
     - a news update
     - a covid data update
    """
    # Initiate national data from spreadsheet
    try:
        csv_filename = path.join(
            get_config("resource_path"),
            get_config("inital_national_data_filename")
        )

        covid_csv_data = covid_data_handler.parse_csv_data(csv_filename)
        national_cases, national_hospital_cases, national_cum_deaths = (
            covid_data_handler.process_covid_csv_data(covid_csv_data)
        )

        covid_data_handler.covid_data['nationalCases7Days'] = national_cases
        covid_data_handler.covid_data['nationalHospitalCases'] = national_hospital_cases
        covid_data_handler.covid_data['nationalCumDeaths'] = national_cum_deaths

        log_debug(f"Loaded initial data: {str(covid_data_handler.covid_data)}")
    except Exception as err:
        log_error("Unexpected error", err)

    # Schedule an initial update
    covid_data_handler.schedule_covid_updates(time.time(), "Initial Covid Update", repeat=False)
    covid_news_handler.schedule_news_updates(time.time(), "Initial News Update", repeat=False)

# Don't run this code if the module is just imported
if __name__ == '__main__':
    main()
    app.run()
