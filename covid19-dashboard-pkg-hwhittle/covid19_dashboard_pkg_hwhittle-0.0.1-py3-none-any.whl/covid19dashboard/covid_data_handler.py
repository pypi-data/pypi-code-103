"""covid_data_handler

This module is used for everything related to fetching
and processing covid data.

It exports the following functions
 * parse_csv_data(csv_filename) -> returns a list of strings for each row in the file
 * process_covid_csv_data(covid_csv_data)
    -> returns number of cases in the last 7 days, current number of hospital cases
       and the cumulative number of deaths
 * schedule_covid_updates(update_interval, update_name, repeat=False, absolute=True)
    -> schedules a covid data update at the given time interval

It exports the following variables
 * covid_data : dictionary
    {
        nationalCases7Days : number
            -> number of new national COVID-19 cases in the last 7 days
        nationalHospitalCases : number
            -> current number of national hospitalised COVID-19 cases
        nationalCumDeaths : number
            -> current cumulative number of national deaths due to COVID-19

        localCases7Days : number
            -> number of new local COVID-19 cases in the last 7 days
    }

It defines the following internal functions
 * covid_API_request(location = "Exeter", location_type = "ltla")
    -> Returns the latest covid data from the UK Covid-19 API as an object
 * find_first_valid_entry(data: List[Dict], key: str)
    -> Finds the first index in the list where key is not None
 * calculate_7_day_cases(data: List[Dict])
    -> Given a list of covid data, it will return the sum of the last 7 days of
        valid case data
 * perform_covid_update()
    -> Handles calling covid_API_request and then updating the covid_data global.
"""

from typing import Dict, List
from uk_covid19 import Cov19API

from .config import get_config
from .logger import log_debug, log_info
from .scheduler import queue_task

# Initial state
covid_data = {
    "nationalCases7Days": 0,
    "nationalHospitalCases": 0,
    "nationalCumDeaths": 0,

    "localCases7Days": 0
}

def parse_csv_data(csv_filename: str) -> List[str]:
    """
    Returns the data rows from a csv file.

    Parameters
    ----------
    csv_filename : str
        The file location of the csv file

    Returns
    -------
    lines : List[str]
        A list of strings for each row in the file
    """

    with open(csv_filename, 'r', encoding='UTF-8') as file:
        return file.readlines()


def find_first_valid_entry(data: List[Dict], key: str) -> int:
    """
    Finds the first index in the list where key is not None

    Parameters
    ----------
    data : List[Dict]
        The list of data
        Data must contain the key given as a parameter

    key : str
        The key to check

    Returns
    -------
    int
        Index of the first valid entry
    """
    i = 0
    while i < len(data) and (data[i][key] is None or data[i][key] == ""):
        i += 1

    return None if i == len(data) else i

def process_covid_csv_data(file_lines: List[str]):
    """
    Returns the number of cases in the last 7 days, current number of hospital
    cases and the cumulative number of deaths based on the given data

    Parameters
    ----------
    file_lines : List[str]
        Covid CSV data as an array of strings, representing each line of the file

    Returns
    -------
    number
        number of cases in the last 7 days

    number
        current number of hospital cases

    number
        cumulative number of deaths
    """
    covid_csv_data = []

    # We ignore the first line since it only contains headers
    for line in file_lines[1:]:
        # rstrip should remove any trailing whitespace from the file.
        covid_csv_data.append(
            line.rstrip().split(",")
        )

    # Skip header and first two entries, sum up the cases of the last 7 days
    # Default to 0 if no value can be found
    num_cases = 0
    first_valid_case_index = find_first_valid_entry(covid_csv_data, 6) + 1
    if first_valid_case_index is not None:
        # We do this to ensure the loop does not cause an index error
        max_index = min(first_valid_case_index + 7, len(covid_csv_data) - 1)
        for i in range(first_valid_case_index, max_index):
            num_cases += int(covid_csv_data[i][6])

    hospital_cases = 0
    first_hospital_cases_index = find_first_valid_entry(covid_csv_data, 5)
    if first_hospital_cases_index is not None:
        hospital_cases = int(covid_csv_data[first_hospital_cases_index][5])

    cumulative_deaths = 0
    first_cum_death_index = find_first_valid_entry(covid_csv_data, 4)
    if first_cum_death_index is not None:
        cumulative_deaths = int(covid_csv_data[first_cum_death_index][4])

    return num_cases, hospital_cases, cumulative_deaths


def covid_API_request(location = "Exeter", location_type = "ltla") -> Dict:
    """
    Returns the latest covid data from the UK Covid-19 API as an object

    Parameters
    ----------
        https://coronavirus.data.gov.uk/details/developers-guide/main-api#params-filters

    location : str
        default = "Exeter"
        The location in which to query data from

    location_type : str
        default = "ltla"
        The type of location used:
            - overview
            - nation
            - region
            - nhsRegion
            - utla
            - ltla


    Returns
    -------
    object
        Response data

        Below is an example of response data
        {
            'data': [
                {
                    'date': '2021-11-02',
                    'areaName': 'England',
                    'areaCode': 'E92000001',
                    'newCasesBySpecimenDate': 547,
                    'hospitalCases': 7362,
                    'cumDailyNsoDeathsByDeathDate': 141544
                },
                ...
            ],
            'lastUpdate': '2021-11-02T11:04:34.587Z',
            'length': 140,
            'totalPages': 1
        }

    """

    log_debug(f"Requesting COVID data for {location} with type {location_type}")

    filters = [
        f"areaType={location_type}",
        f"areaName={location}"
    ]

    api = Cov19API(
        filters = filters,
        structure = {
            "date": "date",
            "areaName": "areaName",
            "areaCode": "areaCode",
            "newCasesBySpecimenDate": "newCasesBySpecimenDate",
            "hospitalCases": "hospitalCases",
            "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate"
        }
    )

    data = api.get_json()

    # Since the data we need is either cumulative or within a short time period,
    # we don't need to worry about pagination.

    log_debug(f"Sucessfully retrieved COVID data for {location} with type {location_type}")

    return data

def calculate_7_day_cases(data: List[Dict]) -> int:
    """
    Given a list of covid data, it will return the sum of the
    last 7 days of valid case data.

    Parameters
    ----------
    data : List[Dict]
        A list of covid data
        The dictionary should contain
         - newCasesBySpecimenDate : int | None

    Returns
    -------
    int
        The cumulative number of cases over 7 days
    """
    log_debug("Calculating 7 day cases")

    cumulative_cases = 0
    first_valid_index = find_first_valid_entry(data, 'newCasesBySpecimenDate')

    for j in range(first_valid_index + 1, first_valid_index + 8):
        cumulative_cases += data[j]['newCasesBySpecimenDate']

    return cumulative_cases

def perform_covid_update() -> None:
    """
    Handles calling covid_API_request and then updating the covid_data global.

    It uses & modifies the covid_data global variable.
    """
    log_info("Performing covid data update...")

    local_response = covid_API_request(get_config('location'), get_config('location_type'))
    nation_response = covid_API_request(get_config('nation_location'), 'nation')

    if local_response['data']:
        local_data = local_response['data']

        covid_data['localCases7Days'] = calculate_7_day_cases(local_data)

    if nation_response['data']:
        nation_data = nation_response['data']

        # hospital cases can be None
        first_hospital_index = find_first_valid_entry(nation_data, 'hospitalCases')
        if first_hospital_index is not None:
            covid_data['nationalHospitalCases'] = nation_data[first_hospital_index]['hospitalCases']

        covid_data['nationalCases7Days'] = calculate_7_day_cases(nation_data)

        # I experienced issues where the first few entries for cumulative deaths were None
        # This should fix that
        first_deaths_index = find_first_valid_entry(nation_data, 'cumDailyNsoDeathsByDeathDate')
        if first_deaths_index is not None:
            covid_data['nationalCumDeaths'] = (
                nation_data[first_deaths_index]['cumDailyNsoDeathsByDeathDate']
            )

def schedule_covid_updates(update_interval: float, update_name: str, repeat=False) -> Dict:
    """
    Schedules a covid update at the given absolute time interval with a given name.

    Parameters
    ----------
    update_interval : number
        The absolute time at which to run the update

    update_name : string
        The name for the update

    repeat : bool
        default -> False
        Whether or not the update should repeat at the given update_interval

    Returns
    -------
    event : Event dictionary
        See scheduler.queue_task
    """

    log_debug(f"Queueing new covid update {update_name}")

    update_entry = queue_task(update_name, perform_covid_update, update_interval, repeat=repeat)

    update_entry['type'] = "Covid"

    log_info(f"Successfully scheduled covid update {update_name}")

    return update_entry
