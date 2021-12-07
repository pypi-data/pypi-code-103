import pytest
from datetime import datetime as dt, timedelta
from assertman.assert_that import that
from assertman.matchers import *


@pytest.mark.parametrize('date', ['2021-11-15T10:45:50',
                                  '1973-11-15T10:45:50.123456',
                                  '13/03/2021 08:58:59',
                                  '03/13/2019 08:58:59',
                                  '15.11.2021 12:15:56',
                                  '2021-11-15 12:15:56',
                                  ])
def test_is_date(date):
    assert that(date).should(is_date())


@pytest.mark.parametrize('date', ['2021-00-00T10:45:50',
                                  '2021-11-15T30:45:50.123456',
                                  '13/03/2019 08:58:59.00',
                                  '03/13/2019 08:58:59.99',
                                  '15.11.2021 12:15:56.000',
                                  '2021-11-15 12:15:56.0',
                                  ])
def test_is_date_negative(date):
    with pytest.raises(AssertionError) as excinfo:
        assert that(date).should(is_date())
    assert "does not match date format" in str(excinfo.value)


@pytest.mark.parametrize("hours_delta", [-1, 0, 1])
@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_today(date_format, hours_delta):
    result_dt = (dt.today() + timedelta(hours=hours_delta)).strftime(date_format)
    assert that(result_dt).should(is_today())


@pytest.mark.parametrize(" days_delta", [-1, 1])
@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_today_negative_1(date_format, days_delta):
    with pytest.raises(AssertionError) as excinfo:
        result_dt = (dt.today() + timedelta(days=days_delta)).strftime(date_format)
        assert that(result_dt).should(is_today())
    assert "Datetime is today" in str(excinfo.value)


@pytest.mark.parametrize("hours_delta", [-1, 0, 1])
@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_tomorrow(date_format, hours_delta):
    result_dt = (dt.today() + timedelta(days=1, hours=hours_delta)).strftime(date_format)
    assert that(result_dt).should(is_tomorrow())


@pytest.mark.parametrize(" days_delta", [0, 2])
@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_tomorrow_negative_1(date_format, days_delta):
    with pytest.raises(AssertionError) as excinfo:
        result_dt = (dt.today() + timedelta(days=days_delta)).strftime(date_format)
        assert that(result_dt).should(is_tomorrow())
    assert "Datetime is tomorrow" in str(excinfo.value)


@pytest.mark.parametrize("hours_delta", [-1, 0, +1])
@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_yesterday(date_format, hours_delta):
    result_dt = (dt.today() + timedelta(days=-1, hours=hours_delta)).strftime(date_format)
    assert that(result_dt).should(is_yesterday())


@pytest.mark.parametrize("days_delta", [-2, 0])
@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_yesterday_negative_1(date_format, days_delta):
    with pytest.raises(AssertionError) as excinfo:
        result_dt = (dt.today() + timedelta(days=days_delta)).strftime(date_format)
        assert that(result_dt).should(is_yesterday())
    assert "Datetime is yesterday" in str(excinfo.value)


@pytest.mark.parametrize("shift_delta", [
    {"weeks": 1},
    {"weeks": 0},
    {"weeks": -1},
    {"days": 1},
    {"days": 0},
    {"days": -1},
    {"hours": 1},
    {"hours": 0},
    {"hours": -1},
])
@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_today_with_shift(date_format, shift_delta):
    result_dt = (dt.today() + timedelta(**shift_delta)).strftime(date_format)
    assert that(result_dt).should(is_today_with_shift(**shift_delta))


@pytest.mark.parametrize("shift_delta, expected_delta", [
    ({"weeks": 1}, {"weeks": 2}),
    ({"weeks": 0}, {"weeks": -1}),
    ({"weeks": -1}, {"weeks": 0}),
    ({"days": 1}, {"days": 2}),
    # ({"days": 0}, {"days": 2}),
    # # ({"days": -1}, {"days": 0}),
    # # ({"hours": 25}, {"hours": 50}),
    # # ({"hours": 0}, {"hours": 24}),
    # # ({"hours": -25}, {"hours": 0}),
])
@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_today_with_shift_negative_1(date_format, shift_delta, expected_delta):
    with pytest.raises(AssertionError) as excinfo:
        result_dt = (dt.today() + timedelta(**shift_delta)).strftime(date_format)
        assert that(result_dt).should(is_today_with_shift(**expected_delta))
    assert "Datetime is today with time shift of" in str(excinfo.value)


@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_greater_than_datetime(date_format):
    expected_datetime = dt.today().strftime(date_format)
    result_datetime = (dt.today() + timedelta(seconds=1)).strftime(date_format)
    assert that(result_datetime).should(is_greater_than_datetime(expected_datetime))


@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_greater_than_datetime_negative_1(date_format):
    with pytest.raises(AssertionError) as excinfo:
        expected_datetime = dt.today().strftime(date_format)
        result_datetime = dt.today().strftime(date_format)
        assert that(result_datetime).should(is_greater_than_datetime(expected_datetime))
    assert "Actual datetime is greater than expected date" in str(excinfo.value)


@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_less_than_datetime(date_format):
    expected_datetime = dt.today().strftime(date_format)
    result_datetime = (dt.today() - timedelta(seconds=1)).strftime(date_format)
    assert that(result_datetime).should(is_less_than_datetime(expected_datetime))


@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_less_than_datetime_negative_1(date_format):
    with pytest.raises(AssertionError) as excinfo:
        expected_datetime = dt.today().strftime(date_format)
        result_datetime = dt.today().strftime(date_format)
        assert that(result_datetime).should(is_less_than_datetime(expected_datetime))
    assert "Actual datetime is less than expected date" in str(excinfo.value)


@pytest.mark.parametrize("mseconds_delta", [-10, 10])
@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    # TODO "%Y-%m-%dT%H:%M:%S.%f",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_equal_to_datetime(date_format, mseconds_delta):
    expected_datetime = dt.today().strftime(date_format)
    result_datetime = (dt.today() + timedelta(milliseconds=mseconds_delta)).strftime(date_format)
    assert that(result_datetime).should(is_equal_to_datetime(expected_datetime))


@pytest.mark.parametrize("seconds_delta", [-1, 1])
@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_equal_to_datetime_negative(date_format, seconds_delta):
    with pytest.raises(AssertionError) as excinfo:
        expected_datetime = dt.today().strftime(date_format)
        result_datetime = (dt.today() + timedelta(seconds=seconds_delta)).strftime(date_format)
        assert that(result_datetime).should(is_equal_to_datetime(expected_datetime))
    assert "Datetimes are equal" in str(excinfo.value)


@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_greater_than_date(date_format):
    expected_datetime = dt.today().strftime(date_format)
    result_datetime = (dt.today() + timedelta(days=1)).strftime(date_format)
    assert that(result_datetime).should(is_greater_than_date(expected_datetime))


@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_greater_than_date_negative_1(date_format):
    with pytest.raises(AssertionError) as excinfo:
        expected_datetime = dt.today().strftime(date_format)
        result_datetime = (dt.today() + timedelta(hours=1)).strftime(date_format)
        assert that(result_datetime).should(is_greater_than_date(expected_datetime))
    assert "Actual date is greater than expected date" in str(excinfo.value)


@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_less_than_date(date_format):
    expected_datetime = dt.today().strftime(date_format)
    result_datetime = (dt.today() - timedelta(days=1)).strftime(date_format)
    assert that(result_datetime).should(is_less_than_date(expected_datetime))


@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_less_than_date_negative_1(date_format):
    with pytest.raises(AssertionError) as excinfo:
        expected_datetime = dt.today().strftime(date_format)
        result_datetime = (dt.today() - timedelta(hours=1)).strftime(date_format)
        assert that(result_datetime).should(is_less_than_date(expected_datetime))
    assert "Actual date is less than expected date" in str(excinfo.value)


@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_equal_to_date(date_format):
    expected_datetime = dt.today().strftime(date_format)
    result_datetime = (dt.today() + timedelta(hours=1)).strftime(date_format)
    assert that(result_datetime).should(is_equal_to_date(expected_datetime))


@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_is_equal_to_date_negative_1(date_format):
    with pytest.raises(AssertionError) as excinfo:
        expected_datetime = dt.today().strftime(date_format)
        result_datetime = (dt.today() + timedelta(days=1)).strftime(date_format)
        assert that(result_datetime).should(is_equal_to_date(expected_datetime))
    assert "Dates are equal" in str(excinfo.value)


@pytest.mark.parametrize("seconds_delta", [-3, 3])
@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_close_to_datetime(date_format, seconds_delta):
    result_datetime = dt.today().strftime(date_format)
    expected_datetime = (dt.today() + timedelta(seconds=seconds_delta)).strftime(date_format)
    assert that(result_datetime).should(close_to_datetime(expected_datetime, seconds=abs(seconds_delta)))


@pytest.mark.parametrize("seconds_delta", [-3, 3])
@pytest.mark.parametrize('date_format', [
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
])
def test_close_to_datetime_negative_1(date_format, seconds_delta):
    with pytest.raises(AssertionError) as excinfo:
        result_datetime = dt.today().strftime(date_format)
        expected_datetime = (dt.today() + timedelta(seconds=seconds_delta)).strftime(date_format)
        assert that(result_datetime).should(close_to_datetime(expected_datetime, seconds=abs(seconds_delta) - 1))

    assert "Dates are equal with margin of error in" in str(excinfo.value)
