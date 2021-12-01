"""[This is a function that creates a flask server and handles the events that occur in it]

"""
from werkzeug.utils import redirect
import datetime
from flask import Flask, render_template, request
from news_data_handling import ARTICLES, scheduler_news, headlines, process_news_api, update_news, logger_news_handler
from covid_data_handler import scheduler_covid, schedule_covid_updates, logger_covid_handler, schedule_update_remove, local_covid_data, national_covid_data
from config import schedule_config, write_json, contents, location
from handlers_logging import logger_interface


app = Flask(__name__)


class MyServer():
    """[A class to create an instance of my flask server]
    """

    def __init__(self) -> None:
        """[My class constructor]
        """
        self.local_covid_data = local_covid_data  # local covid 19 data
        self.national_covid_data = national_covid_data  # national covid 19 data
        self.news_articles = ARTICLES  # news articles
        # run any schedules left in the config file
        self.schedule_widget_handling_running()
        logger_interface.info('contrutor initiatied')

    def home(self) -> object:
        """[My flask decorator function]

        Returns:
            object: [A render function to decorate the template]
        """
        logger_covid_handler.info(scheduler_covid.queue)
        logger_news_handler.info(scheduler_news.queue)
        # run the schedules in the schedulers
        scheduler_covid.run(blocking=False)
        scheduler_news.run(blocking=False)
        ##
        from covid_data_handler import local_covid_data, national_covid_data
        self.local_covid_data = local_covid_data
        self.national_covid_data = national_covid_data
        ##
        from news_data_handling import ARTICLES
        self.news_articles = ARTICLES
        ##
        logger_interface.info('Flask website decorated')
        # the flask decorator
        return render_template('template.html',
                               title='Covid 19 DataHub',
                               location=location,
                               local_7day_infections=self.local_covid_data['7_days_infection'],
                               hospital_cases=self.national_covid_data['Hospital_cases'],
                               deaths_total=self.national_covid_data['Total_deaths'],
                               national_7day_infections=self.national_covid_data['7_days_infection'],
                               nation_location='England',
                               news_articles=self.news_articles,
                               updates=schedule_config,
                               image='covid.jpg')

    def news_widget_handling_removing(self, notif: str) -> None:
        """[A function to add unwanted headlines and later remove them]

        Args:
            notif (str): [The unwanted headlines details]

        Returns:
            [type]: [return back to the home page]
        """
        if notif is None:
            return redirect('/')
        # add the new unwanted articles to the config file
        headlines.append(notif)
        write_json(contents)
        # process ARTICLES so that unwanted articles are removed
        self.news_articles = process_news_api(self.news_articles)
        logger_interface.info('article removed')
        return redirect('/')

    def time_handler(self, time_set: str) -> int:
        """[A function to return the difference of 2 times in seconds]

        Args:
            time_set (str): [The schedules set time]

        Returns:
            int: [The time difference]
        """
        current_time = (datetime.datetime.now()).strftime("%H:%M")
        # calculate the time delay between the two times provided
        time_delay = (datetime.datetime.strptime(time_set, '%H:%M') -
                      datetime.datetime.strptime(current_time, '%H:%M')).seconds
        logger_interface.info('schedule time calculated')
        return time_delay  # return the calculated time delay

    def schedule_widget_handling_running(self) -> None:
        """[A function that executes the schedules in the config file]
        """
        for sched in schedule_config:  # go through each schedule in the schedules list
            update_type = sched['type']
            time_delay = int(self.time_handler(sched['content'][0]))
            title = sched['title']
            repeat = sched['repeat']
            if repeat == True:  # if the schedule is a repeat add 24hrs
                time_delay += 86400
            # the schedule is for both news and covid updates
            if update_type == ["news", "covid-data"]:
                update_news(title, time_delay)
                schedule_covid_updates(time_delay, title)
            elif update_type == ["news"]:  # the schedule is for news updates
                update_news(title, time_delay)
            else:  # the schedule is for covid updates
                schedule_covid_updates(time_delay, title)
            logger_interface.info('new schedule created and running')

    def schedule_widget_handling_removing_user(self, update_item: int) -> None:
        """[A function to both remove schedules from a list and scheduler by a users action]

        Args:
            update_item (int): [The schedule needing removal]
        """
        try:  # trying if the schedule is for both news and covid updates
            for sched in scheduler_covid.queue:
                if sched.kwargs['update_name'] == update_item:
                    # cancel the schedule from the queue
                    scheduler_covid.cancel(sched)
            for sched in scheduler_news.queue:
                if sched.kwargs['update_name'] == update_item:
                    # cancel the schedule from the queue
                    scheduler_news.cancel(sched)
        except:  # the schedule is for covid updates or news updates
            try:  # the schedule is for covid updates
                for sched in scheduler_covid.queue:
                    if sched.kwargs['update_name'] == update_item:
                        # cancel the schedule from the queue
                        scheduler_covid.cancel(sched)
            except:  # the schedule is for news updates
                for sched in scheduler_news.queue:
                    if sched.kwargs['update_name'] == update_item:
                        # cancel the schedule from the queue
                        scheduler_news.cancel(sched)
        # remove the schedule from the schedule list
        schedule_update_remove(update_item)
        logger_interface.info('schedule removed')

    def check_schedule_present(self, title: str):
        """[A function to see if a schedule name already exists]

        Args:
            title (str): [The schedules name]

        Returns:
            [bool]: [present or not]
        """
        for sched in schedule_config:
            if title == sched['title']:  # the schedule name is already in use
                logger_interface.info('schedule title is already present')
                return True

    def schedule_dictionary_format(self, title: str, type: str, content: str, repeat=False) -> dict:
        """[This is a function to create a dictionary out of provided data]

        Args:
            title (str): [the schedules title]
            type (str): [the tyep of schedules it is]
            content (str): [the data about the schedule]
            repeat (bool, optional): [Does the schedule repeat]. Defaults to False.

        Returns:
            [dict]: [a dictionary containing the schedules data]
        """
        Dict_frame = {}
        Dict_frame['title'] = title
        Dict_frame['type'] = type
        if repeat == False:
            try:
                content.remove('repeat')
            except:
                pass
        Dict_frame['content'] = content
        Dict_frame['repeat'] = repeat
        return Dict_frame

    def updates_wiget_handling_storing(self, update: dict) -> None:
        """[A function that will store a new schedule in a schedule list]

        Args:
            update (dict): [The new schedules details]
        """
        Dict_frame = {}
        # check if new schedule has an incorrect name
        if self.check_schedule_present(update['two']):
            logger_interface.info('schedule already in schedul_config')
            return
        try:
            # calculate the type of update that the schedule will be
            type = []
            try:
                type.append(update['news'])
                type.append(update['covid-data'])
            except:
                type = []
                try:
                    type.append(update['covid-data'])
                except:
                    type.append(update['news'])
            try:
                repeat = update['repeat']
                if repeat:  # check if the new schedule is set to repeat
                    update_repeat = update
                    sched_repeat = self.schedule_dictionary_format(
                        update_repeat['two'] + ' repeat', type, list(update_repeat.values()), True)
                    # add the schedule to the schedule list
                    schedule_config.append(sched_repeat)
                    sched_no_repeat = self.schedule_dictionary_format(
                        update['two'], type, list(update.values()))
                    # add the schedule to the schedule list
                    schedule_config.append(sched_no_repeat)
                    logger_interface.info('schedule added to schedul_config')
            except:
                sched_no_repeat = self.schedule_dictionary_format(
                    update['two'], type, list(update.values()))
                # add the schedule to the schedule list
                schedule_config.append(sched_no_repeat)
                logger_interface.info('schedule added to schedul_config')
            write_json(contents)  # add the schedule to the config file
        except:
            logger_interface.error('No data inputted in schedule form')

        self.schedule_widget_handling_running()  # run the schedules

    def widget_handler(self) -> None:
        """[A function to route the flow of data and actions from URL /index/]

        Returns:
            [type]: [return to the decorator]
        """
        query_sched = request.args.get(
            'update_item')  # arg from deleting a schded on website
        query_articles = request.args.get('notif')
        query_update = dict(request.args)
        if query_sched is not None:  # the user action is schedule removal
            logger_interface.info('user demands sched removal')
            self.schedule_widget_handling_removing_user(query_sched)
        elif query_articles is not None:  # the action is news removal
            logger_interface.info('user demands news removal')
            self.news_widget_handling_removing(query_articles)
        elif query_update != {}:  # the user wants to add a new schedule
            logger_interface.info('user demands new schedule to be added')
            self.updates_wiget_handling_storing(query_update)
        return redirect('/')  # go back to the home page


if __name__ == '__main__':
    # creating an instance of my flask server
    server = MyServer()
    # Adding URL rules so that when the URL meets a certain requirement a function is executed
    app.add_url_rule('/', view_func=server.home)
    app.add_url_rule('/index/', view_func=server.widget_handler)
    app.run(debug=True)
    logger_interface.info('Server running')
