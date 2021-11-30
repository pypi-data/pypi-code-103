import re
from typing import Union, Optional, Callable

from pandas import DataFrame
from pandas import MultiIndex
from pandas import to_datetime
from numpy import nan

from ..content import fundamental
from ..content import historical_pricing
from ..core.session import get_default
from ..tools import fields_arg_parser, universe_arg_parser
from ..content.historical_pricing._hp_data_provider import EventTypes

from .get_data import ADC_PATTERN
from .get_data import _look_for_two_exceptions
from .get_data import _add_flag
from .get_data import _create_default_df
from .get_data import _find_and_rename_duplicated_columns
from .get_data import _send_request
from .get_data import _convert_date_columns_to_datetime
from .get_data import _rename_column_n_to_column

EVENTS_INTERVALS = ["tick", "tas", "taq"]

INTERVALS = {
    "tick": {"event_types": None, "adc": "D"},
    "tas": {"event_types": EventTypes.TRADE, "adc": "D"},
    "taq": {"event_types": EventTypes.QUOTE, "adc": "D"},
    "minute": {"pricing": "PT1M", "adc": "D"},
    "1min": {"pricing": "PT1M", "adc": "D"},
    "5min": {"pricing": "PT5M", "adc": "D"},
    "10min": {"pricing": "PT10M", "adc": "D"},
    "30min": {"pricing": "PT30M", "adc": "D"},
    "60min": {"pricing": "PT60M", "adc": "D"},
    "hourly": {"pricing": "PT1H", "adc": "D"},
    "1h": {"pricing": "PT1H", "adc": "D"},
    "daily": {"pricing": "P1D", "adc": "D"},
    "1d": {"pricing": "P1D", "adc": "D"},
    "1D": {"pricing": "P1D", "adc": "D"},
    "7D": {"pricing": "P7D", "adc": "W"},
    "7d": {"pricing": "P7D", "adc": "W"},
    "weekly": {"pricing": "P1W", "adc": "W"},
    "1W": {"pricing": "P1W", "adc": "W"},
    "monthly": {"pricing": "P1M", "adc": "M"},
    "1M": {"pricing": "P1M", "adc": "M"},
    "quarterly": {"pricing": "P3M", "adc": "CQ"},
    "3M": {"pricing": "P3M", "adc": "CQ"},
    "6M": {"pricing": "P6M", "adc": "CS"},
    "yearly": {"pricing": "P1Y", "adc": "CY"},
    "1Y": {"pricing": "P1Y", "adc": "CY"},
}


def get_history(
    universe: Union[str, list],
    fields: Union[str, list, None] = None,
    interval: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    adjustments: Optional[str] = None,
    count: Optional[int] = None,
) -> DataFrame:
    """
    With this tool you can request historical data from Pricing and ADC

    Parameters
    ----------
        universe: str | list
            instruments to request.
        fields: str | list, optional
            fields to request.
        interval: str, optional
            The consolidation interval. Supported intervals are:
            tick, tas, taq, minute, 1min, 5min, 10min, 30min, 60min, hourly, 1h, daily,
            1d, 1D, 7D, 7d, weekly, 1W, monthly, 1M, quarterly, 3M, 6M, yearly, 1Y
        start: str, optional
            The start date and timestamp of the query in ISO8601 with UTC only
        end: str,
            The end date and timestamp of the query in ISO8601 with UTC only
        adjustments : str, optional
            The adjustment
        count : int, optional
            The maximum number of data returned. Values range: 1 - 10000

    Returns
    -------
    pandas.DataFrame

     Examples
    --------
    >>> get_history(universe="GOOG.O")
    >>> get_history(universe="GOOG.O", fields="tr.Revenue", interval="1Y")
    >>> get_history(
    ...     universe="GOOG.O",
    ...     fields=["BID", "ASK", "tr.Revenue"],
    ...     interval="1Y",
    ...     start="2015-01-01",
    ...     end="2020-10-01",
    ... )
    """

    if interval not in INTERVALS and interval is not None:
        raise ValueError(
            f"Not supported interval value.\nSupported intervals are:"
            f"{list(INTERVALS.keys())}"
        )

    _pricing_events = historical_pricing.events.Definition
    _pricing_summaries = historical_pricing.summaries.Definition

    _fundamental_data = fundamental.Definition
    params = {
        "universe": universe,
        "fields": fields,
        "interval": interval,
        "start": start,
        "end": end,
        "adjustments": adjustments,
        "count": count,
    }

    return _get_history(
        p_events=_pricing_events,
        p_summaries=_pricing_summaries,
        adc=_fundamental_data,
        params=params,
    )


def _get_history(
    p_events: Callable,
    p_summaries: Callable,
    adc: Callable,
    params: dict,
) -> DataFrame:
    logger = get_default().logger()

    universe = universe_arg_parser.get_list(params["universe"])
    is_multiuniverse = len(universe) > 1

    adc_df = DataFrame()
    _add_flag(adc_df)

    pricing_df = DataFrame()
    _add_flag(pricing_df)

    adc_params = _translate_pricing_params_to_adc(params)

    if params["interval"] in EVENTS_INTERVALS:
        p_provider = p_events
        interval = params.pop("interval")
        params["eventTypes"] = INTERVALS[interval]["event_types"]
        index_name = "Timestamp"

    else:
        p_provider = p_summaries

        if params["interval"] is not None:
            params["interval"] = INTERVALS[params["interval"]]["pricing"]
        index_name = "Date"

    if params["fields"]:
        fields = fields_arg_parser.get_list(params["fields"])

        adc_fields = [i for i in fields if re.match(ADC_PATTERN, i)]
        pricing_fields = [i for i in fields if i not in adc_fields]

        if adc_fields:
            adc_default_df = _create_default_df(universe, adc_fields)
            adc_df = _send_request(
                data_provider=adc,
                params={
                    "universe": universe,
                    "fields": adc_fields,
                    "parameters": adc_params,
                },
                logger=logger,
                default_df=adc_default_df,
            )
        else:
            _add_flag(adc_df, {"raise_exception": True, "exception": ""})

        if pricing_fields:
            pricing_default_df = _create_default_pricing_df(
                universe, pricing_fields, is_multiuniverse
            )
            params["fields"] = pricing_fields
            pricing_df = _send_request(
                data_provider=p_provider,
                params=params,
                logger=logger,
                default_df=pricing_default_df,
            )
            _remove_field_if_not_requested(
                "EVENT_TYPE", pricing_fields, pricing_df, is_multiuniverse
            )
        else:
            _add_flag(pricing_df, {"raise_exception": True, "exception": ""})

    else:
        pricing_df = _send_request(
            data_provider=p_provider,
            params=params,
            logger=logger,
        )
        _add_flag(adc_df, {"raise_exception": True, "exception": ""})

    _look_for_two_exceptions(pricing_df, adc_df)

    if pricing_df.empty:
        result = adc_df
    elif adc_df.empty:
        result = pricing_df
    else:
        result = _merge(
            pricing_df, adc_df, index_name=index_name, multiindex=is_multiuniverse
        )

    result.ohlc = _ohlc.__get__(result, None)

    return result


def _translate_pricing_params_to_adc(p_params: dict) -> dict:
    adc_params = {}

    if p_params["start"]:
        adc_params["SDate"] = p_params["start"]

    if p_params["end"]:
        adc_params["EDate"] = p_params["end"]

    if p_params["interval"]:
        adc_params["FRQ"] = INTERVALS[p_params["interval"]]["adc"]

    return adc_params


def _merge(
    pricing_df: DataFrame, adc_df: DataFrame, index_name: str, multiindex: bool = False
) -> DataFrame:
    date_column = "Date"

    duplicated_columns = _find_and_rename_duplicated_columns(adc_df)

    if date_column in duplicated_columns:
        date_column = f"{date_column}_0"

    _convert_date_columns_to_datetime(adc_df, pattern="Date")

    adc_df.drop_duplicates(inplace=True)

    if multiindex:
        if adc_df.flags.exception_event["raise_exception"]:
            adc_df = adc_df.pivot(columns="Instrument")
        else:
            adc_df = adc_df.pivot(index=date_column, columns="Instrument")

        adc_df = adc_df.swaplevel(axis=1)

        result = pricing_df.join(adc_df, how="outer")
        result.sort_index(axis=1, inplace=True)
    else:
        adc_df.pop("Instrument")

        if not adc_df.flags.exception_event["raise_exception"]:
            adc_df.set_index(date_column, inplace=True)

        universe = pricing_df.columns.name

        result = pricing_df.merge(
            adc_df, left_index=True, right_index=True, how="outer"
        )

        result.columns.name = universe

    result.dropna(how="all", inplace=True)

    for i in duplicated_columns:
        _rename_column_n_to_column(i, result, multiindex=multiindex)

    result.index.name = index_name
    return result


def _create_default_pricing_df(
    universe: list,
    fields: Optional[list] = None,
    multiindex: bool = False,
) -> DataFrame:
    if multiindex:
        columns = []
        for u in universe:
            for f in fields:
                columns.append((u, f))

        df = DataFrame(
            columns=MultiIndex.from_tuples(columns), index=[to_datetime(nan)]
        )
    else:
        df = DataFrame(columns=fields, index=[to_datetime(nan)])
        df.columns.name = universe[0]

    return df


def _ohlc(self, interval: str = "1min") -> DataFrame:
    df = self.fillna(method="ffill")
    df.fillna(method="bfill", inplace=True)
    df = df.astype("float")

    return df.resample(interval).ohlc()


def _remove_field_if_not_requested(
    field_name: str, fields_list: list, df: DataFrame, multiindex: bool
) -> None:
    if not df.empty and field_name not in set(i.upper() for i in fields_list):
        level = 1 if multiindex else None
        df.drop(field_name, axis=1, level=level, inplace=True, errors="ignore")
