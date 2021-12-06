"""test_covid_data_handler module

This module exports functions which test the covid_data_handler functions.

Some functions have not been tested since they use functions out of my control.

These functions are:
 - covid_API_request
 - perform_covid_update
 - schedule_covid_updates
"""

from covid19dashboard.covid_data_handler import (
    parse_csv_data,
    process_covid_csv_data,
    find_first_valid_entry,
    calculate_7_day_cases
)

def test_parse_csv_data():
    """
    This test ensures parse_csv_data returns the correct number of results.
    """
    data = parse_csv_data('./resources/nation_2021-10-28.csv')
    assert len(data) == 639

def test_process_covid_csv_data():
    """
    This test ensures process_covid_csv_data correctly processes the csv data.
    """
    last7day_cases, current_hospital_cases, total_deaths = process_covid_csv_data(
        parse_csv_data('./resources/nation_2021-10-28.csv')
    )
    assert last7day_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

def test_find_first_valid_entry():
    """
    This test ensures that find_first_valid_entry returns the index of the first
    value that is not None
    """
    test_data = [
        [None],
        [None],
        [True]
    ]

    result = find_first_valid_entry(test_data, 0)

    assert result == 2

def test_calculate_7_day_cases():
    """
    This test ensures that calculate_7_day_cases correctly calculates the cumulative
    cases in the last 7 days.
    """
    test_data = [
        {
            "newCasesBySpecimenDate": None
        },
        {
            "newCasesBySpecimenDate": -1
        },
        {
            "newCasesBySpecimenDate": 1
        },
        {
            "newCasesBySpecimenDate": 2
        },
        {
            "newCasesBySpecimenDate": 3
        },
        {
            "newCasesBySpecimenDate": 4
        },
        {
            "newCasesBySpecimenDate": 5
        },
        {
            "newCasesBySpecimenDate": 6
        },
        {
            "newCasesBySpecimenDate": 7
        },
    ]

    result = calculate_7_day_cases(test_data)

    assert result == 28
