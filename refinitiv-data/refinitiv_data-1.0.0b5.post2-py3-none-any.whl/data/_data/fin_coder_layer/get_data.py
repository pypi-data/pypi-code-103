import re
import sys

import pandas as pd
from typing import Union, Callable, Optional
from pandas import DataFrame, merge, Series
from logging import Logger
from collections import Counter

from ..content import fundamental
from ..core.session import get_default
from ..errors import RDError
from ..tools import fields_arg_parser
from ..pricing.pricing import Stream


# re for ADC fields like started with "TR." case is ignored
ADC_PATTERN = re.compile(r"^tr\..+", re.I)

# re for ADC date fields ended witH ".date" case is ignored
ADC_DATE_PATTERN = re.compile(r"^.+\.date$", re.I)

# re for finding expressions inside ADC fields like
# "TR.F.TotRevPerShr(SDate=0,EDate=-2,Period=FY0,Frq=FY).date"
ADC_PARAM_IN_FIELDS = re.compile(r".*\(.+\).*")

NOT_ALLOWED_SNAPSHOT_FIELDS = ["Date"]


def get_data(
    universe: Union[str, list],
    fields: Union[str, list, None] = None,
    parameters: Union[str, dict, None] = None,
) -> DataFrame:
    """
    With this tool you can request data from ADC, realtime pricing data or
    combination of both;

    Parameters
    ----------
        universe: str | list ,
            instruments to request.
        fields: str | list .
            fields to request.
        parameters: str | dict,
            Single global parameter key=value or dictionary
            of global parameters to request.


    Returns
    -------
    pandas.DataFrame

     Examples
    --------
    >>> get_data(universe=['IBM.N', 'VOD.L'], fields=['BID', 'ASK'])
    >>> get_data(
    ...     universe=['GOOG.O', 'AAPL.O'],
    ...     fields=['TR.EV','TR.EVToSales'],
    ...     parameters = {'SDate': '0CY', 'Curn': 'CAD'}
    ...)
    >>> get_data(
    ...     universe=['IBM.N', 'VOD.L'],
    ...     fields=['BID', 'ASK', 'TR.Revenue'],
    ...     parameters = {'SCale':6, 'SDate':0, 'EDate':-3, 'FRQ':'FY'}
    ...)
    """
    return _get_data(
        _fundamental_data=fundamental.Definition,
        _pricing_stream=Stream(universe=universe, fields=fields),
        universe=universe,
        fields=fields,
        parameters=parameters,
    )


def _get_data(
    _fundamental_data: Callable, _pricing_stream: Stream, **kwargs
) -> DataFrame:
    universe = kwargs.pop("universe")
    logger = get_default().logger()
    fields = kwargs.pop("fields")

    adc_df = DataFrame()
    _add_flag(adc_df)

    pricing_df = DataFrame()
    _add_flag(pricing_df)

    is_parameters_requested = False

    if fields:
        fields = fields_arg_parser.get_list(fields)
        parameters = kwargs.pop("parameters")

        adc_fields = [i for i in fields if re.match(ADC_PATTERN, i)]

        pricing_fields = [
            i
            for i in fields
            if (i not in adc_fields) and (i not in NOT_ALLOWED_SNAPSHOT_FIELDS)
        ]

        is_parameters_in_adc = any(
            i for i in adc_fields if re.match(ADC_PARAM_IN_FIELDS, i)
        )
        is_parameters_requested = parameters or is_parameters_in_adc

        if adc_fields:
            adc_default_df = _create_default_df(universe, adc_fields)

            adc_df = _send_request(
                data_provider=_fundamental_data,
                params={
                    "universe": universe,
                    "fields": adc_fields,
                    "parameters": parameters,
                },
                logger=logger,
                default_df=adc_default_df,
            )
        else:
            _add_flag(adc_df, {"raise_exception": True, "exception": ""})

        if pricing_fields:
            pricing_default_df = _create_default_df(universe, pricing_fields)
            pricing_df = _get_snapshot(
                _pricing_stream, pricing_fields, logger, pricing_default_df
            )
        else:
            _add_flag(pricing_df, {"raise_exception": True, "exception": ""})

    else:
        pricing_df = _get_snapshot(_pricing_stream, fields, logger, pricing_df)
        _add_flag(adc_df, {"raise_exception": True, "exception": ""})

    _look_for_two_exceptions(pricing_df, adc_df)

    if pricing_df.empty:
        result = adc_df
    elif adc_df.empty:
        result = pricing_df
    elif is_parameters_requested and _both_flags_false(pricing_df, adc_df):
        result = _custom_merge(adc_df, pricing_df)
    else:
        result = merge(pricing_df, adc_df)

    return result


def _send_request(
    data_provider: Callable,
    params: dict,
    logger: Logger,
    default_df: DataFrame = DataFrame(),
) -> DataFrame:
    log_string = f"Fields: {params['fields']} for {params['universe']}"
    logger.info(f"Requesting {log_string} \n")
    df = default_df

    try:
        response = data_provider(**params).get_data()
    except Exception:
        logger.exception(f"Failure sending request with {data_provider}")
        df.flags.exception_event = {
            "raise_exception": True,
            "exception": sys.exc_info()[:2],
        }
    else:
        logger.info(
            f"Request to {response.request_message.url.path} with {log_string}\n"
            f"status: {response.status}\n"
        )

        # this check can be removed after all API would return
        # dataframe in response or raise exception
        if response.data.df is not None:
            df = response.data.df
            df.flags.exception_event = {"raise_exception": False, "exception": None}
        else:
            df.flags.exception_event = {
                "raise_exception": True,
                "exception": response.status,
            }

    return df


def _rename_column_n_to_column(
    name: str, df: DataFrame, multiindex: bool = False, level: int = 1
) -> None:
    if multiindex:
        occurrences = (
            # fr"^{name}_\d+$" - searching columns like f"{name}_0", f"{name}_1"
            i
            for i in df.columns.levels[level]
            if re.match(fr"^{name}_\d+$", i)
        )
    else:
        occurrences = (i for i in df.columns if re.match(fr"^{name}_\d+$", i))

    df.rename(columns={i: name for i in occurrences}, inplace=True)


def _rename_column_to_column_n(name: str, df: DataFrame) -> None:
    new_names = []
    count = 0
    for i in df.columns:
        if i == name:
            i = f"{i}_{count}"
            count += 1
        new_names.append(i)
    df.columns = new_names


def _custom_merge(df_1: DataFrame, df_2: DataFrame) -> DataFrame:
    date_column = "Date"
    instruments_column = "Instrument"

    duplicated_columns = _find_and_rename_duplicated_columns(df_1)

    if date_column in duplicated_columns:
        date_column = f"{date_column}_0"

    _convert_date_columns_to_datetime(df_1, pattern="Date")

    latest_rows_indexes = df_1.groupby(instruments_column)[date_column].idxmax(
        skipna=False
    )
    _remove_empty_rows(latest_rows_indexes)

    latest_info = df_1.loc[latest_rows_indexes]

    mediator = pd.merge(df_2, latest_info, how="outer")
    result = pd.merge(mediator, df_1, how="right")

    for i in duplicated_columns:
        _rename_column_n_to_column(i, result)

    return result


def _get_snapshot(
    stream: Stream,
    fields: Optional[list],
    logger: Logger,
    default_df: DataFrame = DataFrame(),
) -> Optional[DataFrame]:
    logger.info(f"Requesting pricing info for fields={fields} via websocket\n")
    df = default_df

    try:
        stream.open(with_updates=False)
        df = stream.get_snapshot(fields=fields)
        stream.close()
    except Exception:
        logger.exception(f"Failure retrieving snapshot form {stream}")
        df.flags.exception_event = {
            "raise_exception": True,
            "exception": sys.exc_info()[:2],
        }
    else:
        df.flags.exception_event = {"raise_exception": False, "exception": None}

    return df


def _convert_date_columns_to_datetime(df: DataFrame, pattern: str) -> None:
    for i in df.columns:
        if pattern in i:
            df[i] = pd.to_datetime(df[i])


def _find_and_rename_duplicated_columns(df: DataFrame) -> list:
    counted_columns = Counter(df.columns)
    duplicated_columns = [i for i, n in counted_columns.items() if n > 1]

    for i in duplicated_columns:
        _rename_column_to_column_n(i, df)

    return duplicated_columns


def _remove_empty_rows(series: Series) -> None:
    for name, value in series.items():
        if pd.isna(value):
            series.pop(name)


def _create_default_df(
    universe: list,
    fields: Optional[list] = None,
) -> DataFrame:
    df = DataFrame(
        {
            "Instrument": {n: i for n, i in enumerate(universe)},
            **{i: {} for i in fields},
        }
    )
    return df


def _look_for_two_exceptions(df_1: DataFrame, df_2: DataFrame) -> None:
    if (
        df_1.flags.exception_event["raise_exception"]
        and df_2.flags.exception_event["raise_exception"]
    ):
        ex1 = df_1.flags.exception_event["exception"]
        ex2 = df_2.flags.exception_event["exception"]

        raise RDError(1, f"\nNo data to return, please check errors:\n{ex1}\n{ex2}\n")


def _add_flag(df: DataFrame, flag: Optional[dict] = None) -> None:
    if flag is None:
        flag = {"raise_exception": False, "exception": ""}
    df.flags.exception_event = flag


def _both_flags_false(df_1: DataFrame, df_2: DataFrame) -> bool:
    return (
        not df_1.flags.exception_event["raise_exception"]
        and not df_2.flags.exception_event["raise_exception"]
    )
