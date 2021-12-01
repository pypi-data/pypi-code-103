"""[This is a module that handles the collection and processing of covid data from a API or file]

"""
import sched
import time
from uk_covid19 import Cov19API
from config import schedule_update_remove, location
from handlers_logging import logger_covid_handler

# covid scheduler
scheduler_covid = sched.scheduler(time.time, time.sleep)


def schedule_event(update_name: str) -> None:
    """[A fucntion to execute a scheduled event]

    Args:
        update_name (str): [The schedules name]
    """
    global local_covid_data
    global national_covid_data
    # update the local covid data variable
    local_covid_data = process_covid_json_data(covid_API_request(location))
    national_covid_data = process_covid_json_data(covid_API_request(
        'England', 'Nation'))  # update the national covid data
    # remove the schedule from the schedule list
    schedule_update_remove(update_name)
    logger_covid_handler.info('schedule removed from scheduler_covid')


def schedule_covid_updates(update_interval: int, update_name: str) -> None:
    """[A function to create a schedule]

    Args:
        update_interval (int): [The schedules time delay]
        update_name (str): [The schedules name]
    """
    scheduler_covid.enter(update_interval, 1, schedule_event, kwargs={
        'update_name': update_name})  # Add the schedule to the coivd scheduler
    logger_covid_handler.info('schedule added to scheduler_covid')


def find_latest_json_data(json_data: list, key: str) -> int:
    """[A function to find the first None value in a list]

    Args:
        json_data (list): [The data being searched]
        key (str): [The data of that data being searched]

    Returns:
        int: [The first value that is not a None value]
    """
    value = 0
    for data in json_data:
        if data[key] != None:
            value = data[key]  # the first none type entry
            return value
    if value == 0:
        return value


def cumulative_data(json_data: list) -> int:
    """[A funtction to find the total for data over the past 7 days]

    Args:
        json_data (list): [the data being added up]

    Returns:
        int: [the accumulated data]
    """
    i = 0
    total = 0
    count = 0
    while count != 7:
        if json_data[i]["Daily Cases"] is None:
            if count == 0:
                count += 1
                i += 1
        if json_data[i]["Daily Cases"] is None:
            json_data[i]["Daily Cases"] = 0
        total += int(json_data[i]["Daily Cases"])
        count += 1
        i += 1
    return total  # return the cumulative data


def process_covid_json_data(covid_json_data: dict) -> dict:
    """[A function to process API data collected as a JSON file]

    Args:
        covid_json_data (dict): [The JSON file]

    Returns:
        dict: [A dictionary of the processed covid data]
    """
    location_type = covid_json_data['location type']
    seven_days_cases = 0
    current_hospital_cases = 0
    total_deaths = 0
    count = 0
    covid_json_data = covid_json_data['data']
    dict_frame = {}
    if covid_json_data != []:
        if location_type == 'Nation':  # The API request is national
            current_hospital_cases = find_latest_json_data(
                covid_json_data, "New Hospital Admssions")
            total_deaths = find_latest_json_data(
                covid_json_data, "Cumulative Deaths")
            seven_days_cases = cumulative_data(covid_json_data)
        else:  # The API request is ltla
            current_hospital_cases = find_latest_json_data(
                covid_json_data, "New Hospital Admssions")
            total_deaths = find_latest_json_data(
                covid_json_data, "Cumulative Deaths")
            seven_days_cases = cumulative_data(covid_json_data[1:])
    dict_frame['7_days_infection'] = seven_days_cases
    dict_frame['Hospital_cases'] = current_hospital_cases
    dict_frame['Total_deaths'] = total_deaths
    logger_covid_handler.info('JSON API covid data processed')
    return dict_frame  # Return the processed data


def covid_API_request(location: str = 'Exeter', location_type: str = 'ltla') -> dict:
    """[A function to request covid API data]

    Args:
        location (str, optional): [location for API data]. Defaults to 'Exeter'.
        location_type (str, optional): [location type for API data]. Defaults to 'ltla'.

    Returns:
        dict: [A dictionary of the processed API data]
    """
    location_filter = [f"areaType={location_type}", f'areaName={location}']
    cases_filter = 'newCasesBySpecimenDate'
    if location_type == 'Nation':
        cases_filter = 'newCasesByPublishDate'
    covid_info_category = {"Area Code": "areaCode",
                           "Area Name": "areaName",
                           "Area Type": "areaType",
                           "Date": "date",
                           "Cumulative Deaths": "cumDailyNsoDeathsByDeathDate",
                           "New Hospital Admssions": "hospitalCases",
                           "Daily Cases": cases_filter, }
    covid_api = Cov19API(filters=location_filter,
                         structure=covid_info_category)  # call the API request
    covid_live_data_json = covid_api.get_json()  # get the API data in a json format
    logger_covid_handler.info('Covid API data collected')
    # return the processed API data
    covid_live_data_json['location type'] = location_type
    return covid_live_data_json


def find_latest_entry(covid_data: list, index: int) -> int:
    """[A functiont to find the first element that isnt '']

    Args:
        covid_data (list): [A list of covid data]
        index (int): [The column that we are looking in]

    Returns:
        int: [The first entry that insn't '']
    """
    found = False
    i = 1
    while found is not True:
        if i == (len(covid_data)-1):
            return 0
        if covid_data[i][index] != '':
            latest_entry = covid_data[i][index]  # The first none type data
            found = True
        i += 1
    return int(latest_entry)


def process_covid_csv_data(covid_csv_data: list) -> int:
    """[A function that processes a csv file of covid data]

    Args:
        covid_csv_data (list): [the csv files data]

    Returns:
        int: [the processed data]
    """
    seven_days_cases = 0
    current_hospital_cases = 0
    total_deaths = 0
    i = 1
    counter = 0
    while counter != 7:
        if covid_csv_data[i][6] != '':
            if counter == 0:
                i += 1
            seven_days_cases += int(covid_csv_data[i][6])
            counter += 1
        i += 1
    total_deaths = find_latest_entry(covid_csv_data, 4)
    current_hospital_cases = find_latest_entry(covid_csv_data, 5)
    logger_covid_handler.info('Covid CSV file processed')
    # return the processed covid 19 data
    return seven_days_cases, current_hospital_cases, total_deaths


def parse_csv_data(csv_filename: str) -> list:
    """[A function to open and format a csv file]

    Args:
        csv_filename (str): [the cvs filename]

    Returns:
        list: [A list containing the csv data]
    """
    csv_filename = open(csv_filename, 'r', encoding='UTF-8').readlines()
    csv_list = []
    for line in csv_filename:
        line = line.rstrip()
        line = line.split(',')
        csv_list.append(line)  # append each line of the csv file to a list
    logger_covid_handler.info('csv file opened and formatted')
    return csv_list  # return the csv file in a list format


# assign my global variables the news API requests
local_covid_data = process_covid_json_data(covid_API_request(location))
national_covid_data = process_covid_json_data(covid_API_request(
    'England', 'Nation'))
