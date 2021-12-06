from canalyst_candas.utils import (
    Getter,
    LogFile,
    CsvDataKeys,
    SCENARIO_URL,
    calendar_quarter,
    crawl_company_pages,
    create_drivers_dot,
    df_filter,
    dot_parse,
    filter_dataset,
    get_api_headers,
    get_company_info_from_ticker,
    get_data_set_from_mds,
    get_drivers_from_api,
    get_name_index_from_csv,
    get_forecast_url,
    get_forecast_url_data,
    get_model_info,
    get_request,
    get_scenario_url_data,
    json_to_df,
    map_scenario_urls,
    read_json,
    save_guidance_csv,
    send_scenario,
    calendar_quarter,
    get_excel_model,
)
import __main__
from pyvis.network import Network
from functools import reduce
import networkx as nx
import plotly.express as px
from statistics import stdev
import os.path
import time
import requests
import numpy as np
import datetime
import io

import pandas as pd
import sys
import json
import re

import matplotlib.pyplot as plt
import matplotlib.image as image
import matplotlib.font_manager as fm

plt.style.use("fivethirtyeight")

from requests.models import Response
from typing import Dict
from urllib.parse import quote_plus
from io import StringIO

import boto3
import os
import string
import urllib3
from os import path

from joblib import Parallel, delayed

import multiprocessing

num_cores = multiprocessing.cpu_count()

urllib3.disable_warnings()
from openpyxl import load_workbook, styles
from pathlib import Path

from canalyst_candas.configuration.config import Config
from canalyst_candas.settings import CONFIG
from canalyst_candas import settings


def help():
    """
    Canalyst Candas help function
    """
    print("Canalyst Candas help")
    print(
        "Please go to https://pypi.org/project/canalyst-candas/#description for installation help"
    )
    print("For support, please contact jed.gore@canalyst.com")
    print("For an API KEY please go to https://app.canalyst.com/u/settings/api-tokens")
    print("For an Excel model download:get_excel_model(ticker, config)")


class FuncMusic(object):
    """
    Helper class for on the fly function generation.

    Used in the ForecastFrame concept where we try to change one param
    across multiple tickers for re-fit in the scenario engine.
    """

    def apply_function(self, value, modifier, argument):
        self.value = value
        self.modifier = modifier
        self.argument = argument
        method_name = "func_" + str(self.modifier)
        method = getattr(
            self,
            method_name,
            lambda: "Invalid function: use add, subtract, divide, or multiply",
        )
        return method()

    def func_add(self):
        return float(self.value) + float(self.argument)

    def func_divide(self):
        return float(self.value) / float(self.argument)

    def func_multiply(self):
        return float(self.value) * float(self.argument)

    def func_subtract(self):
        return float(self.value) - float(self.argument)


class Search:
    def __init__(self, config: Config = None):
        self.config = config
        self.df_search = None
        self.df_guidance = None
        self.ticker_list = None

    def remove_stopwords(self, sentence):
        my_stopwords = [
            "in",
            "Change",
            "YoY",
            ",",
            "%",
            "(Calculated)",
            "(QoQ)",
            "QoQ",
            "mm",
        ]
        tokens = sentence.split(" ")
        tokens_filtered = [word for word in tokens if not word in my_stopwords]
        tokens_filtered = [
            "".join(c for c in s if c not in string.punctuation)
            for s in tokens_filtered
        ]
        return (" ").join(tokens_filtered)

    def get_ticker_list(self, ticker=""):
        if self.ticker_list is None:
            GET = Getter(config=self.config)
            path_name = f"DATA/cwl20.csv"
            df = GET.get_csv_from_s3(path_name)
            df = df.drop(columns=["CSIN"])
            self.ticker_list = df
        else:
            df = self.ticker_list
        if ticker != "":
            df = df.loc[df["Bloomberg Ticker"] == ticker]
        return df

    def help(self):
        print("search_time_series syntax:")
        print(
            "ticker (Bloomberg ticker),sector,time_series_name,time_series_description,category,is_driver,unit_type"
        )
        print("unit types:currency, percentage, count, ratio, time")
        print("search_guidance_time_series syntax:")
        print(
            "ticker (Bloomberg ticker),sector,time_series_description,time_series_name,most_recent (True or blank)"
        )
        return

    def search_guidance_time_series(
        self,
        ticker="",
        sector="",
        file_name="",
        time_series_name="",
        time_series_description="",
        query="",
        most_recent="",
    ):
        if self.df_guidance is None:
            body = Getter(config=self.config).get_zip_csv_from_s3(
                f"DATA/df_guidance.zip"
            )
            self.df_guidance = pd.read_csv(io.StringIO(body), low_memory=False)

        df = self.df_guidance
        df = df.loc[df["Type.1"] == "Estimate"]

        df = df.rename(
            columns={"Item": "time_series_description", "Item Name": "time_series_name"}
        )

        if most_recent == True:
            df = df.sort_values(["ticker", "time_series_name", "Date"], ascending=False)
            df = df.groupby(["ticker", "time_series_name"]).first().reset_index()

        if type(ticker) == list:
            df = df.loc[df["ticker"].isin(ticker)]
        elif ticker != "":
            df = df.loc[df["ticker"] == ticker]

        if sector != "":
            df = df.loc[df["Path"].str.contains(sector, case=True, regex=True)]
        if time_series_name != "":
            df = df.loc[
                df["time_series_name"].str.contains(
                    time_series_name, case=False, regex=True
                )
            ]

        if time_series_description != "":

            ts_lower = time_series_description.lower()
            split_strings = ts_lower.split(" ")
            df["ts_lower"] = df["time_series_description"].str.lower()
            df["search_matches"] = df["ts_lower"].str.count("|".join(split_strings))
            df = df.loc[df["search_matches"] > 0]

        else:
            df["search_matches"] = 1

        if file_name != "":
            df = df.loc[df["Filename"].str.contains(file_name, case=False)]

        df = df[
            [
                "ticker",
                # "CSIN",
                "Path",
                "Filename",
                "time_series_description",
                "time_series_name",
                "Fiscal Period",
                "Low",
                "Mid",
                "High",
                "Type.1",
                "Date",
                "Link",
                "search_matches",
            ]
        ].sort_values(
            ["search_matches", "ticker", "Date", "time_series_name"], ascending=False
        )

        if query != "":
            df = df.query(query)
            df = df.sort_values(["search_matches", "value"], ascending=False)
        return df

    def match_time_series(self, ticker="", time_series=""):
        if type(time_series) == "str":
            time_series = [time_series]

        df_list = []
        for item in time_series:
            df = self.search_time_series(ticker=ticker, time_series_description=item)
            df["target"] = item
            df_list.append(df)

        return pd.concat(df_list)

    def search_time_series_excel(
        self, ticker="", time_series_name="", time_series_description=""
    ):
        pd.options.mode.chained_assignment = None
        if self.df_search is None or stream_data == True:
            print("Building search index...")
            body = Getter(config=self.config).get_zip_csv_from_s3(
                f"DATA/df_search_excel.zip"
            )

        df_list = []
        chunksize = 100000

        for chunk in pd.read_csv(
            io.StringIO(body),
            usecols=[
                "ticker",
                "time_series_description",
                "time_series_name",
            ],
            chunksize=chunksize,
        ):
            if type(ticker) == list:
                if len(ticker[0]) > 0:
                    df = chunk.loc[chunk["ticker"].isin(ticker)]
                else:
                    df = chunk
            elif ticker != "":
                print(ticker)
                df = chunk.loc[chunk["ticker"] == ticker]
            else:
                df = chunk

            if time_series_name != "":
                df = df.loc[
                    df["time_series_name"].str.contains(
                        time_series_name, case=False, regex=True
                    )
                ]

            if time_series_description != "":

                ts_lower = time_series_description.lower()

                split_strings = ts_lower.split(" ")
                df["ts_lower"] = df["time_series_description"].str.lower()
                df["search_matches"] = df["ts_lower"].str.count("|".join(split_strings))
                df = df.drop(columns=["ts_lower"])
                df = df.loc[df["search_matches"] > 0]

            else:
                df["search_matches"] = 1

            if df.shape[0] > 0:
                df_list.append(df)
            df = None
            chunk = None

        if len(df_list):
            df = pd.concat(df_list)

        df = df[
            [
                "ticker",
                "time_series_description",
                "time_series_name",
                "search_matches",
            ]
        ].sort_values(
            ["search_matches", "ticker", "time_series_description"], ascending=False
        )
        return df

    def search_time_series(
        self,
        ticker="",
        sector="",
        time_series_name="",
        time_series_description="",
        category="",
        is_driver="",
        file_name="",
        unit_type="",
        mo_only=False,
        exact_match=False,
        period_duration_type="",
        query="",
    ):
        pd.options.mode.chained_assignment = None
        if self.df_search is None:
            print("Building search index...")
            body = Getter(config=self.config).get_zip_csv_from_s3(f"DATA/df_search.zip")
            self.df_search = pd.read_csv(
                io.StringIO(body),
                usecols=[
                    "ticker",
                    "CSIN",
                    "Filename",
                    "Path",
                    "category",
                    "time_series_description",
                    "time_series_name",
                    "is_driver",
                    "period_duration_type",
                    "unit_type",
                    "value",
                ],
            )

        df = self.df_search

        if type(ticker) == list:
            df = df.loc[df["ticker"].isin(ticker)]
        elif ticker != "":
            df = df.loc[df["ticker"] == ticker]

        if mo_only == True:
            df = df.loc[df["time_series_name"].str.startswith("MO_")]

        if sector != "":
            df = df.loc[df["Path"].str.contains(sector, case=True, regex=True)]

        if category != "":
            df = df.loc[df["category"].str.contains(category, case=True, regex=True)]

        if time_series_name != "":
            if exact_match == True:
                df = df.loc[
                    df["time_series_name"] == time_series_name
                ]  # dont lowercase this
            else:
                df = df.loc[
                    df["time_series_name"].str.contains(
                        time_series_name, case=False, regex=True
                    )
                ]

        if time_series_description != "":

            ts_lower = time_series_description.lower()
            if exact_match == True:
                df = df.loc[df["time_series_description"].str.lower() == ts_lower]
            else:
                split_strings = ts_lower.split(" ")
                df["ts_lower"] = df["time_series_description"].str.lower()
                df["search_matches"] = df["ts_lower"].str.count("|".join(split_strings))
                df = df.drop(columns=["ts_lower"])
                df = df.loc[df["search_matches"] > 0]
        else:
            df["search_matches"] = 1

        if is_driver != "":
            df = df.loc[df["is_driver"] == is_driver]

        if unit_type != "":
            df = df.loc[
                df["unit_type"] == unit_type
            ]  # currency, percentage, count, ratio, time

        if period_duration_type != "":
            df["period_duration_type"] = np.where(
                df["value"].isna(), "fiscal_year", "fiscal_quarter"
            )

        # if df.shape[0] > 0:
        #    df_list.append(df)
        # df = None
        # chunk = None

        df["period_duration_type"] = np.where(
            df["value"].isna(), "fiscal_year", "fiscal_quarter"
        )

        df = df[
            [
                "ticker",
                "CSIN",
                "Path",
                "Filename",
                "category",
                "time_series_description",
                "time_series_name",
                "period_duration_type",
                "unit_type",
                "is_driver",
                "value",
                "search_matches",
            ]
        ].sort_values(
            ["search_matches", "ticker", "time_series_description"], ascending=False
        )
        if query != "":
            df = df.query(query)
            df = df.sort_values(["search_matches", "value"], ascending=False)
        return df


# WIP Class for parsing json revenue builds in graph structure (as opposed to tree)
# class FormulaGraph:
# def __init__(
#     self,
#     file_name=None,
#     ticker=None,
#     auto_parse=True,
#     force=False,  # determines if the file json file will be force pulled from s3
# ):

#     # Raise an error if a ticker or file name is not entered
#     if not ticker and not file_name:
#         raise ValueError(
#             "You must pass in a value for either the ticker "
#             "argument or file_name argument"
#         )
#     elif ticker and file_name:
#         raise ValueError(
#             "Only pass in a value for ticker OR file_name, not both. "
#             "If you pass a ticker, the data will be pulled from s3. "
#             "If you pass a file_name, the data will be pulled from that json file."
#         )

#     # Set json_file instance var if a valid file was passed
#     self.json_file = ""
#     if os.path.isfile(file_name):
#         self.json_file = file_name
#     else:
#         raise ValueError(
#             f"The value you passed for file_name, {file_name}, is not a valid"
#             "JSON file"
#         )

#     # set instance variables
#     self.ticker = ticker
#     self.auto = auto_parse
#     self.force = force
#     self.node_dict = self.read_json()  # dictionary of all nodes in the tree

#     # instance variables to be set in parse_formula_graph()
#     self.formula_strings = (
#         {}
#     )  # use dynamic programming/memoization to store the formula strings of each node in the tree
#     self.drivers = {}  # drivers and their values
#     self.labels = {}  # node: time_series_description

#     # automatically create string representation and code expression (without custom drivers)
#     if auto_parse:
#         # create a string representation of the precedent formula and dictionary of drivers, and compile into code expression
#         self.parse_formula_graph()

# # return the node dictionary from the json file
# def read_json(self):
#     with open(self.json_file) as f:
#         return json.load(f)["NodeDict"]

# def parse_formula_graph(self):
#     # by default we will parse the first cell in the json
#     cell = list(self.node_dict.values())[0]

#     self.string_representation = self.calculate_formula_string(cell)

# # recursive method which calculates the formula string of the given cell/node
# def calculate_formula_string(
#     self, cell: dict  # dictionary with info for the given cell
# ):

#     # cells id's are in the formula mo_name|period, so replace the vertical line with an underscore
#     # and the "-" in the period
#     cell_id = cell["Id"].replace("|", "_").replace("-", "_")

#     # base case: if the cell is a driver or has no precedents (bottom of tree)
#     if cell["PrecedentIds"] == []:
#         # add drivers to the dictionary of drivers, replace the value of non drivers with their values
#         if cell["IsDriver"]:
#             self.drivers[cell_id] = float(cell["Value"])
#             self.labels[cell_id] = cell["TimeSeriesDescription"]

#             to_return = cell_id
#         else:
#             v = cell["Value"]
#             if v is None:
#                 v = "0.0"
#             to_return = v

#         return f"({to_return})"

#     # get formula of this cell
#     if cell["Formula"]:
#         formula = cell["Formula"].replace("=", "")
#         formula = formula[0].replace("+", "") + formula[1:]

#     # change ^ (exp in excel) to ** (exp in python)
#     formula = formula.replace("^", "**")

#     if len(cell["PrecedentIds"]) > 2:
#         print("test")

#     # recursive case: replace each cell in this cells formula with that cells formula
#     for prec_cell_id in cell["PrecedentIds"]:

#         prec_cell = self.node_dict[prec_cell_id]
#         val_to_replace = prec_cell["SimpleAddress"]

#         # if formula has not been memoized, calculate it
#         if prec_cell_id not in self.formula_strings:
#             self.formula_strings[prec_cell_id] = self.calculate_formula_string(
#                 prec_cell
#             )

#         # Currently, each cell does not reference each of it's precedent cells, so:
#         # In order to solve this I would have to loop through each cell id in formula_strings and
#         # replace its simple address with its formula string, which would mean slower runtime here
#         val_to_insert = self.formula_strings[prec_cell_id]

#         # replace the cell address with its formula
#         if val_to_replace in formula:
#             # use re.sub with \bstr\b to only replace exactly that formula
#             formula = re.sub(
#                 r"\b" + val_to_replace + r"\b", f"({val_to_insert})", formula
#             )

#     return formula

# # evaluate the code derived from the string using the drivers default passed in values
# def evaluate_node(self, node_id=None, drivers=None):
#     # default to using the normal drivers
#     if type(drivers) != dict:
#         drivers = self.drivers
#     else:
#         drivers = {
#             **self.drivers,
#             **drivers,
#         }  # replace drivers with passed in values

#     functions = {
#         "SUM": lambda *nums: sum(nums),
#         "AVERAGE": lambda *nums: sum(nums) / len(nums),
#         "ROUND": lambda num, decimal_pts: round(num, decimal_pts),
#         "EOMONTH": self.eomonth,
#     }

#     if node_id is None:
#         return eval(self.string_representation, {}, {**drivers, **functions})
#     else:
#         return eval(self.formula_strings[node_id], {}, {**drivers, **functions})

# # mimics excel function needed for evaluating some formula strings
# def eomonth(self, date, num_months):

#     # parsing the date string, only take the first part since all the dates seem to be 12:00:00 AM
#     split_date = date.split()
#     date = split_date[0]

#     # print a message just incase there's a date that's not 12:00:00 AM
#     if " ".join(split_date[1:]) != "12:00:00 AM":
#         print(
#             "time is not 12 am. this might cause an issue"
#             " in the eomonth function in the FormulaTree class"
#         )

#     import calendar

#     def add_months(sourcedate, months):
#         month = sourcedate.month - 1 + months
#         year = sourcedate.year + month // 12
#         month = month % 12 + 1
#         day = min(sourcedate.day, calendar.monthrange(year, month)[1])
#         return datetime.datetime(year, month, day)

#     # create a datetime object out of the date parameter
#     SECONDS_IN_A_DAY = 86400
#     date = datetime.datetime.fromisoformat(date)

#     # add months to the date and get the last date of the month the date is in
#     date = add_months(date, num_months)
#     date = datetime.datetime(
#         (date.year + (date.month // 12)), (date.month + 1) % 12, 1
#     ) - datetime.timedelta(days=1)

#     # return the timestamp as a number of days as opposed to seconds
#     date = datetime.datetime.timestamp(date) / SECONDS_IN_A_DAY
#     return date


# helper class to read a formula json
# class FormulaTree:

# author Sebastian Fisher 6-30-2021
# json created by Ian Paul 2021
# def __init__(
#     self,
#     config: Config = None,
#     file_name=None,
#     ticker=None,
#     auto_parse=True,
#     force=False,
# ):
#     self.config = config or CONFIG
#     self.s3_client = Getter(self.config)
#     if not ticker and not file_name:
#         raise ValueError(
#             "You must pass in a value for either the ticker argument or file_name argument"
#         )
#     elif ticker and file_name:
#         raise ValueError(
#             "Only pass in a value for ticker OR file_name, not both. If you pass a ticker, the data will be pulled from s3. If you pass a file_name, the data will be pulled from that json file."
#         )

#     self.json_file = ""
#     self.ticker = ticker
#     if ticker:
#         # get rid of country symbol from ticker
#         ticker = ticker.split()[0]
#         # file on s3
#         from_filename = f"DATA/{ticker}/{ticker}_revenue.json"
#         # location to download
#         to_dir = os.path.join(self.config.default_dir, f"DATA/{ticker}")
#         to_filename = os.path.join(to_dir, f"{ticker}_revenue.json")

#         self.json_file = to_filename

#         # if the file doesn't exist, attempt to pull from s3
#         if not os.path.isfile(to_filename) or force:
#             # Make directories to file if they don't exist
#             os.makedirs(to_dir, exist_ok=True)
#             self.s3_client.get_s3_file(to_filename, from_filename)

#     else:
#         if os.path.isfile(file_name):
#             self.json_file = file_name
#         else:
#             raise ValueError(
#                 "The value you passed for file_name,"
#                 f" {file_name}, is not a valid JSON file."
#             )

#     self.auto = auto_parse

#     # These will be set later on in parse_formula_tree
#     self.string_representation = None
#     self.drivers = None
#     self.custom_drivers = None
#     self.driver_labels = None
#     self.formula_code = None
#     self.betas = {}
#     self.cell_formulas = {}

#     # automatically create string representation and code expression (without custom drivers)
#     if auto_parse:
#         # create a string representation of the precedent formula and dictionary of drivers, and compile into code expression
#         self.parse_formula_tree()

# # Find "beta" value for each driver and custom driver
# def find_betas(self):
#     curr_rev = self.evaluate_node()
#     self.betas = self.find_betas_helper(self.drivers, curr_rev)
#     self.betas.update(self.find_betas_helper(self.custom_drivers, curr_rev))

# def find_betas_helper(self, drivers_dict, curr_rev):
#     betas = {}
#     for driver in drivers_dict:
#         curr_val = drivers_dict[driver]
#         new_rev = self.evaluate_node(drivers={driver: curr_val * 1.01})
#         beta = (new_rev - curr_rev) / curr_rev
#         betas[driver] = beta
#     return betas

# # evaluate the code derived from the string using the drivers default passed in values
# def evaluate_node(self, time_series="MO_RIS_REV", drivers=None):
#     # default to using the normal drivers
#     if type(drivers) != dict:
#         drivers = {**self.drivers, **self.custom_drivers}
#     else:
#         drivers = {
#             **self.drivers,
#             **self.custom_drivers,
#             **drivers,
#         }  # replace drivers with passed in values

#     functions = {
#         "SUM": lambda *nums: sum(nums),
#         "AVERAGE": lambda *nums: sum(nums) / len(nums),
#         "ROUND": lambda num, decimal_pts: round(num, decimal_pts),
#         "EOMONTH": self.eomonth,
#     }

#     if time_series == "MO_RIS_REV":
#         return eval(self.formula_code, {}, {**drivers, **functions})
#     else:
#         return eval(self.cell_formulas[time_series], {}, {**drivers, **functions})

# # defining needed excel function
# def eomonth(date, num_months):

#     # parsing the date string, only take the first part since all the dates seem to be 12:00:00 AM
#     split_date = date.split()
#     date = split_date[0]

#     # print a message just incase there's a date that's not 12:00:00 AM
#     if " ".join(split_date[1:]) != "12:00:00 AM":
#         print(
#             "time is not 12 am. this might cause an issue"
#             " in the eomonth function in the FormulaTree class"
#         )

#     import calendar

#     def add_months(sourcedate, months):
#         month = sourcedate.month - 1 + months
#         year = sourcedate.year + month // 12
#         month = month % 12 + 1
#         day = min(sourcedate.day, calendar.monthrange(year, month)[1])
#         return datetime.datetime(year, month, day)

#     # create a datetime object out of the date parameter
#     SECONDS_IN_A_DAY = 86400
#     date = datetime.datetime.fromisoformat(date)

#     # add months to the date and get the last date of the month the date is in
#     date = add_months(date, num_months)
#     date = datetime.datetime(
#         (date.year + (date.month // 12)), (date.month + 1) % 12, 1
#     ) - datetime.timedelta(days=1)

#     # return the timestamp as a number of days as opposed to seconds
#     date = datetime.datetime.timestamp(date) / SECONDS_IN_A_DAY
#     return date

# # Creates a string representation of the formula tree
# def parse_formula_tree(self, custom_drivers_list=[]):

#     # load the file from json
#     with open(self.json_file) as f:
#         cell_data = json.load(f)

#     # Set up a dictionary for the values and labels of each driver variable
#     drivers = {}
#     labels = {}

#     # Set up a dictionary for formula for each node in the tree
#     self.cell_formulas = {}

#     # start out with each custom driver as None value
#     custom_drivers_list = list(custom_drivers_list)
#     custom_drivers = dict((driver, None) for driver in custom_drivers_list)

#     # call function to recur to precedent cells
#     formula = self.create_cell_string_representation(
#         cell_data, drivers, labels, custom_drivers
#     )

#     # set values of instance variables
#     self.string_representation = formula
#     self.drivers = drivers
#     self.custom_drivers = custom_drivers
#     self.driver_labels = labels

#     # compile string representation into code expression
#     self.formula_code = compile(
#         ")\n".join(self.string_representation.split(")")), "<string>", "eval"
#     )

#     # calc betas
#     self.find_betas()

# # creates a string representation of the formula for a given cell json
# def create_cell_string_representation(
#     self, cell_data, drivers, labels, custom_drivers
# ):

#     # get the formula and no_name of the cell from its json
#     if cell_data["Formula"]:
#         formula = cell_data["Formula"].replace("=", "")
#         formula = formula[0].replace("+", "") + formula[1:]

#     cell_mo_name = cell_data["RelationalCellAddress"]
#     cell_mo_name = cell_mo_name[1 : cell_mo_name.find("|")]

#     # Base case: if the cell is a driver, custom driver, or if it is historical,
#     # then return that cells value or variable
#     if (
#         cell_data["PrecedentCellsCount"] == 0
#         or cell_data["IsHistorical"]
#         or cell_mo_name in custom_drivers
#     ):

#         # for drivers, add them to the right dictionary and return the mo name
#         if cell_data["IsDriver"]:
#             drivers[cell_mo_name] = float(cell_data["Value"])

#             labels[cell_mo_name] = cell_data["TimeSeriesDescription"]
#             to_return = cell_mo_name

#         # do the same for custom drivers but with the custom drivers dict
#         elif cell_mo_name in custom_drivers:
#             custom_drivers[cell_mo_name] = float(cell_data["Value"])

#             labels[cell_mo_name] = float(cell_data["Value"])
#             to_return = cell_mo_name

#         # Otherwise return the value of the cell
#         else:
#             v = cell_data["Value"]
#             if v is None:
#                 v = "0.0"
#             to_return = v

#         # making sure date values are adding with quotations around them
#         if cell_data["Formula"] and "EOMONTH" in cell_data["Formula"]:
#             return f'("{to_return}")'
#         return f"({to_return})"

#     # Recursive case: loop through the precedent cells of this cell, and replace
#     # the formula with the string formulas of those cells
#     for prec_cell_data in cell_data["PrecedentCells"]:
#         # set the value to replace (the precedent cell's address)
#         val_to_replace = prec_cell_data["SimpleAddress"]
#         prec_cell_mo_name = prec_cell_data["RelationalCellAddress"]
#         prec_cell_mo_name = prec_cell_mo_name[1 : prec_cell_mo_name.find("|")]

#         # set the value to insert into the formula (the precedent cell's formula)
#         if prec_cell_mo_name not in self.cell_formulas:
#             val_to_insert = self.create_cell_string_representation(
#                 prec_cell_data, drivers, labels, custom_drivers
#             )
#             self.cell_formulas[prec_cell_mo_name] = val_to_insert

#         else:
#             val_to_insert = self.cell_formulas[prec_cell_mo_name]

#         # change ^ (exp in excel) to ** (exp in python)
#         formula = formula.replace("^", "**")

#         # replace the cell address with its formula
#         if val_to_replace in formula:
#             # formula = formula.replace(val_to_replace, f"({val_to_insert})")
#             # use re.sub with \bstr\b to only replace exactly that formula
#             formula = re.sub(
#                 r"\b" + val_to_replace + r"\b", f"({val_to_insert})", formula
#             )

#     return formula


# a class of multiple models
class ModelSet:
    def __init__(
        self,
        ticker_list,
        config: Config = None,
        period_name="Q",
        extract_drivers=True,
        historical_only=False,
        allow_nulls=False,
        company_info=True,
    ):
        self.allow_nulls = allow_nulls
        self.config = config or CONFIG
        self.historical_only = historical_only
        self.period_name = period_name
        self.extract_drivers = extract_drivers
        self.ticker = ticker_list
        self.ticker_list = ticker_list
        self.drivers = None
        self.models = {}
        self.company_info = company_info
        self.api_headers = get_api_headers(self.config.canalyst_api_key)

        self.get_featurelibrary()  # set self._features

        if type(ticker_list) is str:
            ticker_list = [ticker_list]

    def help(self, function_name=""):
        dict_help = {
            "create_model_map": "Create a model map.  params: ticker, col_for_labels = 'time_series_name', time_series_name = 'MO_RIS_REV', tree = True, notebook = True",
            "create_time_series_chart": "Create a time series chart.  params: ticker, time_series_name",
            "guidance": "Return guidance from a mmodel.  params: ticker",
            "mrq": "Return most recent quarter from a mmodel.  params: ticker",
            "time_series_search": "Return time series regex match. params: time_series_name",
            "driver_search": "Return driver regex match. params: driver_name",
            "model_frame": "Return a dataframe of the full modelset. params: time_series_name,period_name,is_driver='',pivot=False,mrq=False,period_duration_type='',is_historical='',n_periods='',mrq_notation=False",
            "forecast_frame": "Return a params dataframe for use in the fit function. params: time_series_name, n_periods, function_name='value', function_value='' where function name can be add, subtract, multiply, divide, or value",
            "fit": "Return a return series for a fitted model. params: params dataframe, return_series.  params dataframe columns are: ticker period time_series_name value new_value",
            "model_set.models[Bloomberg Ticker].get_excel_model_name()": "Return most recent model name for a ticker",
            "model_set.models[Bloomberg Ticker].get_most_recent_model_date()": "Return most recent model upload date for a ticker",
        }
        if function_name != "":
            return dict_help[function_name]
        else:
            df = pd.DataFrame(dict_help, index=[0]).T
            df.columns = ["help"]
            return df

    def plot_guidance(self, ticker, time_series_name):
        if ticker not in self.ticker_list:
            print("Please choose a ticker in this ModelSet")
            return
        self.models[ticker].plot_guidance(time_series_name)
        return

    def pe_dataset(self, ticker, yahoo_ticker, index_ticker="^GSPC", n_periods=24):
        import canalyst_candas.candas_datareader as cdr

        df_earnings = cdr.get_earnings_and_prices(yahoo_ticker, index_ticker)
        if df_earnings is None:
            return None

        df_earnings = df_earnings[
            [
                "ticker",
                "earnings_date",
                "beta_252",
                "alpha_1_day",
                "alpha_5_day",
                "alpha_10_day",
            ]
        ]
        df_earnings = df_earnings.sort_values("earnings_date", ascending=False)

        df_model = self.model_frame(
            ticker=ticker, is_historical=True, period_duration_type="fiscal_quarter"
        )

        edq_list = list(
            cdr.calendar_quarter(df_earnings, "earnings_date", datetime=True)[
                "earnings_date_CALENDAR_QUARTER"
            ]
        )

        mdq_list = list(
            df_model.groupby("period_name_sorted")
            .first()
            .reset_index()
            .sort_values("period_end_date", ascending=False)["period_name_sorted"]
        )

        if len(edq_list) < n_periods:
            n_periods = len(edq_list)
            print(
                "Price earnings dataset using " + str(n_periods) + " periods available"
            )

        d = {
            "earnings_date_q": edq_list[0:n_periods],
            "period_name_sorted": mdq_list[0:n_periods],
        }

        df_dates = pd.DataFrame(d)
        df_model = pd.merge(df_model, df_dates)
        df_earnings["earnings_date_q"] = cdr.calendar_quarter(
            df_earnings, "earnings_date", datetime=True
        )["earnings_date_CALENDAR_QUARTER"]
        df_model["price_ticker"] = yahoo_ticker
        df_model = df_model.drop(columns=["ticker"])
        df_data = pd.merge(
            df_model,
            df_earnings,
            how="inner",
            left_on=["price_ticker", "earnings_date_q"],
            right_on=["ticker", "earnings_date_q"],
        )
        df_data["ticker"] = ticker
        df_data = df_data.drop(
            columns=[
                "earnings_dateshift",
                "earnings_date_CALENDAR_QUARTER",
                "category_type_slug",
                "time_series_slug",
            ]
        )
        return df_data

    def regress_dataframe_time_series_groups(
        self, df_data=None, y_name="alpha_10_day", return_grouped=True
    ):
        ticker = df_data.iloc[0]["ticker"]
        import canalyst_candas.candas_datareader as cdr

        df = cdr.regress_dataframe_groups(
            df_data, y_name=y_name, return_grouped=return_grouped
        )
        df = df.dropna()
        df["ticker"] = ticker
        return df

    def create_model_map(
        self,
        ticker,
        col_for_labels="time_series_name",
        time_series_name="MO_RIS_REV",
        tree=True,
        notebook=False,
    ):
        """
        Returns a tree for the given ticker and time series
        """
        if type(ticker) == list:
            print("Please request one ticker at a time.")
            return

        if ticker in self.ticker_list:
            model = self.models[ticker]
            return model.create_model_map(
                time_series_name=time_series_name,
                tree=tree,
                col_for_labels=col_for_labels,
                notebook=notebook,
                common_time_series_names=self._common_time_series_names,
            )
        else:
            print("Please choose a ticker in this ModelSet's ticker list")
            return

    def create_time_series_chart(
        self, ticker_list="", time_series_name="", historical=False
    ):  # MODELSET
        """
        Create a time series chart for the given ticker and time series
        """

        if ticker_list == "":
            df = self._features

            if type(time_series_name) == list:
                df = df.loc[self._features["time_series_name"].isin(time_series_name)]
            else:
                df = df.loc[self._features["time_series_name"] == time_series_name]

            if historical:
                df = df.loc[df["is_historical"] == historical]

            df = df.loc[df["period_name"].str.contains("Q")].sort_values(
                ["ticker", "period_end_date"]
            )
            df = df.loc[df["period_end_date"] > "2015-01-01"]
            df = df.dropna(subset=["value"])
            # return df
            # df = df.groupby('ticker').size().order(ascending=False).reset_index()

            row1 = df.iloc[0]
            # title = self.ticker + " " + str(row1["time_series_description"])
            xlabel = "Fiscal Quarter"
            # ylabel = row1["time_series_description"]

            colors = {
                "red": "#ff207c",
                "grey": "#C3C2C3",
                "blue": "#00838F",
                "orange": "#ffa320",
                "green": "#00ec8b",
            }

            plt.rc("figure", figsize=(12, 9))

            if type(time_series_name) != list:

                df_plot = df.loc[
                    df["time_series_name"] == time_series_name
                ].sort_values(["ticker", "time_series_name"])

                if ticker_list == "":
                    ticker_list = self.ticker_list
                elif type(ticker_list) == list:
                    ticker_list = ticker_list
                else:
                    ticker_list = [ticker_list]

                for ticker in ticker_list:

                    df_plot_one = df_plot[df_plot["ticker"] == ticker]
                    df_plot_one = df_plot_one.sort_values("period_end_date")
                    df_plot_one = df_plot_one.loc[df_plot_one["value"].notna()]

                    if df_plot_one.shape[0] > 0:
                        plt.plot(
                            df_plot_one["period_end_date"],
                            df_plot_one["value"],
                            label=ticker + " " + time_series_name,
                            linewidth=2,
                        )
                        plt.axvline(
                            x=self.models[ticker].mrq()["period_end_date"][0],
                            color="black",
                        )
            else:
                if ticker_list == "":
                    ticker_list = self.ticker_list
                elif type(ticker_list) == list:
                    ticker_list = ticker_list
                else:
                    ticker_list = [ticker_list]

                for tsn in time_series_name:
                    df_plot = df.loc[df["time_series_name"] == tsn]
                    for ticker in ticker_list:
                        df_plot_one = df_plot[df_plot["ticker"] == ticker]
                        df_plot_one = df_plot_one.sort_values("period_end_date")
                        df_plot_one = df_plot_one.loc[df_plot_one["value"].notna()]
                        if df_plot_one.shape[0] > 0:
                            plt.plot(
                                df_plot_one["period_end_date"],
                                df_plot_one["value"],
                                label=ticker + " " + tsn,
                                linewidth=2,
                            )
                            plt.axvline(
                                x=self.models[ticker].mrq()["period_end_date"][0],
                                color="black",
                            )

            plt.xticks(rotation=90)
            plt.legend()
            plt.show()
            return
        if ticker_list == "":
            ticker_list = self.ticker_list
        elif type(ticker_list) == list:
            ticker_list = ticker_list
        else:
            ticker_list = [ticker_list]

        if time_series_name == "":
            print("Please enter one time_series_name")
            return
        for ticker in ticker_list:
            df = self._features
            if historical:
                df = df.loc[df["is_historical"] == historical]

            df_plot = df.loc[df["time_series_name"] == time_series_name]
            df_plot_one = df_plot[df_plot["ticker"] == ticker]
            df_plot_one = df_plot_one.sort_values("period_end_date")
            df_plot_one = df_plot_one.loc[df_plot_one["value"].notna()]
            if df_plot_one.shape[0] > 0:
                plt.plot(
                    df_plot_one["period_end_date"],
                    df_plot_one["value"],
                    label=ticker + " " + str(time_series_name),
                    linewidth=2,
                )
                plt.axvline(
                    x=self.models[ticker].mrq()["period_end_date"][0],
                    color="black",
                )

        plt.xticks(rotation=90)
        plt.legend()
        plt.show()

        # if ticker in self.ticker_list:
        #    self.models[ticker].create_time_series_chart(time_series_name, historical)
        # else:
        #    print("Please choose a ticker in this ModelSet's ticker list")
        return

    def guidance(self, ticker):
        """
        Get guidance for ticker or list of tickers
        """
        if type(ticker) == list:
            list_df = []
            for t in ticker:
                if ticker in self.ticker_list:
                    df = self.models[ticker].guidance()
                    df["ticker"] = ticker
                    col_name = "ticker"
                    first_col = df.pop(col_name)
                    df.insert(0, col_name, first_col)
                    list_df.append(df)
            return pd.concat(list_df)
        else:
            if ticker in self.ticker_list:
                df = self.models[ticker].guidance()
                df["ticker"] = ticker
                col_name = "ticker"
                first_col = df.pop(col_name)
                df.insert(0, col_name, first_col)
                return df
            else:
                print("Please choose a ticker in this ModelSet's ticker list")
        return

    def mrq(self, ticker):
        """
        Gets the most recent quarter for a ticker or list of tickers
        """
        if type(ticker) == list:
            list_df = []
            for t in ticker:
                if ticker in self.ticker_list:
                    df = self.models[ticker].mrq()
                    df["ticker"] = t
                    list_df.append(df)
            return pd.concat(list_df)
        else:
            if ticker in self.ticker_list:
                return self.models[ticker].mrq()
            else:
                print("Please choose a ticker in this ModelSet's ticker list")
        return

    def time_series_names(self):
        df = self._features
        df = (
            df.groupby(["time_series_name"])
            .first()
            .reset_index()[["time_series_description", "time_series_name"]]
        )
        self.FeatureList = df
        return

    def time_series_search(self, search_term=""):
        """
        Searches for the search term in the default dataframe

        Returns dataframe with columns ['time_series_name','time_series_description','category_slug']
        """
        df = self._features
        if search_term != "":
            df1 = df[
                df["time_series_description"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df2 = df[
                df["time_series_name"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df = pd.concat([df1, df2])
            df = (
                df.groupby(
                    ["time_series_name", "time_series_description", "category_slug"]
                )
                .first()
                .reset_index()
            )
        return df  # [['time_series_name','time_series_description','category_slug']]

    def driver_search(self, search_term="", col="time_series_name"):
        """
        Search model drivers
        """
        df = self.drivers
        if search_term != "":
            df1 = df[
                df["time_series_description"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df2 = df[
                df["time_series_name"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df = pd.concat([df1, df2])
            df = (
                df.groupby(
                    ["time_series_name", "time_series_description", "category_slug"]
                )
                .first()
                .reset_index()
            )
        return df  # [['time_series_name','time_series_description','category_slug']]

    def common_time_series(self):
        """
        Get common time series names
        """
        return self._common_time_series_names

    def get_featurelibrary(self, col="time_series_name"):
        """
        Creates the default dataframe features and drivers
        """
        if type(self.ticker_list) is list:

            list_all = []
            list_df = []
            for ticker in self.ticker_list:
                try:
                    list_rows = []

                    md = Model(
                        config=self.config,
                        ticker=ticker,
                        company_info=self.company_info,
                    )
                    self.models[ticker] = md

                    df = md._model_frame

                    list_df.append(df)

                    if df is not None:
                        list_rows = list(set(list(df[col])))
                        list_all.append(list_rows)

                except:
                    self.ticker_list.remove(ticker)
                    print("Error on ticker " + str(ticker))

            if len(list_df) == 0:
                return

            # df = pd.concat(list_df)
            from itertools import chain

            # faster than concat
            def fast_flatten(input_list):
                return list(chain.from_iterable(input_list))

            COLUMN_NAMES = list_df[0].columns
            df_dict = dict.fromkeys(COLUMN_NAMES, [])
            for col in COLUMN_NAMES:
                extracted = (df[col] for df in list_df)
                # Flatten and save to df_dict
                df_dict[col] = fast_flatten(extracted)

            df = pd.DataFrame.from_dict(df_dict)[COLUMN_NAMES]
            list_df = []
            df_dict = {}

            res = list(reduce(lambda i, j: i & j, (set(x) for x in list_all)))
            self._common_time_series_names = res

            if self.allow_nulls == False:
                df = df_filter(df, "time_series_name", res)
                self._features = df
            else:
                self._features = df

            if self.extract_drivers == True:
                self.drivers = df[df["is_driver"] == 1]
            return

        else:
            try:
                df = Model(
                    config=self.config,
                    ticker_list=self.ticker_list,
                    extract_drivers=self.extract_drivers,
                    historical_only=self.historical_only,
                ).model_frame()
                self._features = df
                if self.extract_drivers == True:
                    self.drivers = df[df["is_driver"] == 1]
            except:
                print("Error on ticker " + str(self.ticker_list))
            return
        return

    # allows for filtering and shaping the default dataframe
    # MODELSET model_frame
    def model_frame(
        self,
        time_series_name="",
        period_name="",
        is_driver="",
        pivot=False,
        mrq=False,
        period_duration_type="",
        is_historical="",
        n_periods="",
        mrq_notation=False,
        unit_type="",
        category="",
        warning=True,
        ticker="",
        n_diff="",
    ):

        if ticker != "":
            df = self.models[ticker]._model_frame
        else:
            df = self._features

        return filter_dataset(
            df,  # this is the core dataset of the modelset class
            time_series_name,
            period_name,
            is_driver,
            pivot,
            mrq,
            period_duration_type,
            is_historical,
            n_periods,
            mrq_notation,
            unit_type,
            category,
            warning,
            n_diff,
        )

    def modify_features(
        self, params, modifier, argument, period_name=""
    ):  # modifier = add,subtract,multiply,divide.  argument is the number to apply.
        if type(params) is not dict:
            print("Params must be a dictionary")
            return
        print("get drivers from model")

        dict_out = {}
        for count, ticker in enumerate(self.ticker_list):

            df = self.models[ticker].default_df.head(1)

            df_filter = self.models[ticker].default_df[
                self.models[ticker].default_df["time_series_name"] == params[ticker]
            ]

            period_name = df_filter["period_name"].iloc[0]
            try:
                old_value = df_filter["value"].iloc[
                    0
                ]  # df_filter[df_filter['period_name']==period_name]['value'][0]
            except:
                continue
            try:
                d = FuncMusic()
                new_value = d.apply_function(old_value, modifier, argument)

            except:
                return df_filter

            dict_out[ticker] = [params[ticker], old_value, new_value, period_name]
        df = pd.DataFrame(dict_out).T.reset_index()
        df.columns = [
            "ticker",
            "time_series_name",
            "default_value",
            "scenario_value",
            "period_name",
        ]
        return df

    def forecast_frame(
        self, time_series_name, n_periods, function_name="value", function_value=""
    ):
        df = self.model_frame(
            [time_series_name],
            period_duration_type="fiscal_quarter",
            is_historical=False,
            n_periods=n_periods,
        )

        if function_name != "value":
            d = FuncMusic()
            df["new_value"] = df.apply(
                lambda row: d.apply_function(
                    row["value"], modifier=function_name, argument=function_value
                ),
                axis=1,
            )
        else:
            df["new_value"] = function_value

        df = df[
            [
                "ticker",
                "period_name",
                "time_series_name",
                "value",
                "new_value",
                "period_end_date",
            ]
        ]

        return df

    # MODELSET fit()
    def fit(self, params, return_series):
        # ticker period time_series_name value new_value
        dict_summary = {}
        if type(params) is dict:
            df = pd.DataFrame.from_dict(params, orient="index").reset_index()
        else:
            df = params

        df_grouped = df.groupby(["ticker"]).first().reset_index()

        dict_data = {}
        for i, row in df_grouped.iterrows():

            df_ticker = df[df["ticker"] == row["ticker"]]
            ticker = row["ticker"]  # .iloc[0]
            self.models[ticker].set_new_uuid()
            list_changes = []

            for i, row in df_ticker.iterrows():
                feature_value = row["new_value"]
                feature_name = row["time_series_name"]
                feature_period = row["period_name"]
                ticker = row["ticker"]

                list_changes.append(
                    {
                        "time_series": feature_name,
                        "period": feature_period,
                        "value_expression": {"type": "literal", "value": feature_value},
                    }
                )

                data = {"changes": list_changes, "name": self.models[ticker].uuid}
                dict_data[ticker] = data

        res = Parallel(n_jobs=num_cores)(
            delayed(send_scenario)(
                ticker,
                data,
                self.api_headers,
                self.models[ticker].csin,
                self.models[ticker].latest_version,
                self.config.mds_host,
            )
            for ticker, data in dict_data.items()
        )

        for resp in res:
            self.models[ticker].record_scenario_url(resp)

        ticker_list = list(set(list(df["ticker"])))

        for ticker in ticker_list:

            try:
                self.models[ticker].model_fit(return_series)
                # try:
                dict_summary[ticker] = self.models[ticker].summary()
            except:
                print("Error on fit for " + return_series)

        return dict_summary

    def filter_summary(self, dict_summary, period_type="Q"):

        pd.set_option("mode.chained_assignment", None)
        pd.set_option("display.float_format", lambda x: "%.5f" % x)

        list_out = []
        for ticker in dict_summary.keys():

            df = dict_summary[ticker]

            list_out.append(df)
        df = pd.concat(list_out)
        df["sort_period_name"] = (
            df["period_name"].str.split("-").str[1]
            + df["period_name"].str.split("-").str[0]
        )
        df = df.sort_values(["ticker", "sort_period_name"])
        df = df[df["period_name"].str.contains(period_type)]
        df = df.drop(columns="sort_period_name")

        return df


class ModelMap:
    def __init__(
        self,
        config: Config = None,
        ticker=None,
        model=None,
        time_series_name="MO_RIS_REV",
        col_for_labels="time_series_name",
        tree=True,
        common_size_tree=True,
        notebook=True,
        auto_download=True,
        tree_complexity_limit=None,  # model map will not display as a tree if its complexity is above this limit
        common_time_series=None,  # optional list of common features. nodes with this feature will be made triangles
    ):
        self.config = config or CONFIG
        self.s3_client = Getter(config=self.config)
        self.api_headers = get_api_headers(self.config.canalyst_api_key)

        if model:
            self.model = model
            self.ticker = self.model.ticker
        elif ticker:
            self.ticker = ticker
            self.model = None
        else:
            raise TypeError("You must pass in either a ticker or model")

        self.time_series = time_series_name
        self.col_for_labels = col_for_labels
        self.tree = tree
        self.common_size_tree = common_size_tree
        self.notebook = notebook
        self.auto_download = auto_download
        self.tree_complexity_limit = tree_complexity_limit
        if common_time_series:
            self.common_time_series = set(common_time_series)
        else:
            self.common_time_series = common_time_series

        # will be defined when create_model is called
        self.dot_file = None
        self.nodes = None
        self.path_distances = None
        self.complexity = None
        self.mean_end_node_distance = 0
        self.max_end_node_distance = 0
        self.std_dev_node_distance = 0

        # Create dataframe for precedent/dependent tree, graph of the tree, and a network of that graph (for visualization)
        self.df = self.load_data()
        try:
            self.network = self.create_model()
        except:
            print(
                "Canalyst-Candas error creating modelmap.  Possible permissions issue with your Canalyst login, please contact us."
            )

        self.fig = None

    def load_data(self) -> pd.DataFrame:
        """
        Helper function to load data from candas

        Loads model_frame for chosen ticker and creates a dot file
        """
        if self.model:
            cdm = self.model
        else:
            cdm = Model(config=self.config, ticker=self.ticker)

        df = cdm.model_frame(period_duration_type="fiscal_quarter", n_periods="")

        self.dot_file = create_drivers_dot(
            self.time_series, self.api_headers, self.ticker, self.config, self.s3_client
        )

        return df

    def create_model(self, toggle_drag_nodes=True):
        """
        Create a model of the dot file and optionally download in an html file
        """
        # read dot file into a graph
        G = nx.drawing.nx_pydot.read_dot(self.dot_file)

        # Create Network from nx graph and turn off physics so dragging is easier
        graph = Network(
            "100%",
            "100%",
            notebook=self.notebook,  # enables displaying in a notebook
            directed=True,  # makes edges arrows
            layout=self.tree,  # Creates tree structure
            bgcolor="#FFFFFF",
        )
        graph.toggle_physics(True)
        graph.from_nx(G)

        # update the complexity of the graph, and if it is greater than the limit, set self.Tree to False
        # won't do anything if tree_complexity_limit wasn't set
        self.complexity = len(graph.nodes)
        if self.tree_complexity_limit and self.complexity > self.tree_complexity_limit:
            self.tree = False

        # model_frame filtered with only needed time_series
        time_series = {}
        for node in graph.nodes:
            id_split = node["id"].split("|")
            if len(id_split) > 1:
                time_series[id_split[0]] = id_split[1]

        df = self.df[self.df["time_series_slug"].isin(time_series)]

        # root node id
        root_id = graph.nodes[0]["id"]

        # column to use for labels
        col_for_labels = self.col_for_labels

        # reformat nodes
        # path lengths between each node
        self.path_distances = dict(nx.all_pairs_shortest_path_length(G))
        num_drivers = 0
        distances = []

        for node in graph.nodes:

            # set level of node based on distance from root
            node["level"] = self.path_distances[root_id][node["id"]]

            # parse node id into time series slug and period name
            # AND get row with the given period and time series slug in dataframe
            id_split = node["id"].split("|")

            ###### SOLVE FOR MODELS CONTAINING MO.Lastprice (which is not in candas dataframe)
            # account for time series without a period (last price)
            if len(id_split) < 2:
                node["title"] = node["label"]
                continue
            ######

            slug = id_split[0]

            period = id_split[1]
            rows = df[df["period_name"] == period]

            row = rows[rows["time_series_slug"] == slug].iloc[0]

            # format colors of nodes and update data
            if row["is_driver"]:
                color = "rgba(200, 0, 0, 0.75)"

                ########## STATS #############
                # get dist from root node, add to mean and find new max
                distance_from_root = self.path_distances[root_id][node["id"]]
                distances.append(distance_from_root)
                self.mean_end_node_distance += distance_from_root
                if distance_from_root > self.max_end_node_distance:
                    self.max_end_node_distance = distance_from_root
                num_drivers += 1
                ##########
            else:
                color = "rgba(0, 0, 200, 0.75)"
            node["color"] = color

            # make the node a triangle if the it is one of the common_time_series
            if (
                self.common_time_series
                and row["time_series_name"] in self.common_time_series
            ):
                node["borderWidth"] = 5
                node["shape"] = "triangle"

            # store description, mo_name, ticker, and driver status of time series in node
            node["description"] = str(row["time_series_description"])
            node["time_series_name"] = str(row["time_series_name"])
            node["ticker"] = str(row["ticker"])
            node["is_driver"] = str(row["is_driver"])

            # set the label to be whatever column the user decided to take labels from
            label = str(row[col_for_labels])
            # Format the label to be max n characters per line
            n = 13  # characters per line
            new_label = "\n".join([label[i : i + n] for i in range(0, len(label), n)])
            node["label"] = new_label

            # add value and units and ismm (time_series_description) attributes to node for future use
            node["amount"] = row["value"]
            node["units"] = row["unit_type"]
            node["ismm"] = ", mm" in row["time_series_description"]

            # Add value to node label
            value = ""
            if node["units"] == "currency":
                value = ":\n{}{:,.2f}".format(row["unit_symbol"], row["value"])
            elif node["units"] == "percentage":
                value = ":\n{:.2f}{}".format(row["value"], row["unit_symbol"])
            # elif node["units"] == "count":
            #     value = ":\n{:.2f} {}".format(row["value"], row["unit_symbol"])
            # elif node["units"] == "ratio":
            #     value = ":\n{:.2f} {}".format(row["value"], row["unit_symbol"])
            # elif node["units"] == "time":
            #     value = ":\n{:.2f} {}".format(row["value"], row["unit_symbol"])
            else:
                value = ":\n{:.2f} {}".format(row["value"], row["unit_symbol"])
            node["label"] += value

            # title is label without newlines
            node["title"] = node["label"].replace("\n", "")

        # reformat edges
        for edge in graph.edges:
            temp = edge["from"]
            edge["from"] = edge["to"]
            edge["to"] = temp
            # label the edge with percentages
            if self.common_size_tree:
                precedent = graph.get_node(edge["from"])
                dependent = graph.get_node(edge["to"])

                # WORKAROUND FOR MO.Lastprice ##################
                if "|" not in precedent["id"] or "|" not in dependent["id"]:
                    continue
                ################################################

                if (
                    precedent["units"] == "currency"
                    and precedent["ismm"]
                    and dependent["ismm"]
                    and precedent["level"] != dependent["level"]
                ):
                    if np.isnan(precedent["amount"]):
                        pct = 0
                    else:
                        pct = precedent["amount"] / dependent["amount"] * 100
                    edge["label"] = "{:.2f}%".format(pct)

        # reformat tree so desired time series is at the root and it is a different color
        root = graph.get_node(root_id)
        root.update({"color": "rgba(0, 200, 0, 0.75)", "size": 40})

        if self.notebook:
            graph.width, graph.height = "1000px", "1000px"

        # toggles node dragging and disables physics
        graph.toggle_drag_nodes(toggle_drag_nodes)
        graph.toggle_physics(False)

        # make sure models folder exists
        models_folder = os.path.join(
            os.path.dirname(os.path.abspath(__name__)), "models"
        )
        if not os.path.isdir(models_folder):
            os.mkdir(models_folder)

        # create path for model in models folder adjacent to this file
        model_path = os.path.join(
            self.config.default_dir,
            f"DATA/{self.ticker.split()[0]}/{self.ticker.split()[0]}_{self.time_series}_model_map.html",
        )
        self.model_path = os.path.relpath(
            model_path, start=os.path.abspath(os.path.dirname(__main__.__name__))
        )

        if self.auto_download:
            graph.write_html(self.model_path, notebook=self.notebook)

        self.nodes = graph.nodes
        self.edges = graph.edges

        # update stats
        self.mean_end_node_distance /= num_drivers
        self.std_dev_node_distance = stdev(distances)

        return graph

    def show(self):
        """
        Shows the model map
        """
        return self.network.show(self.model_path)

    def create_node_df(self):
        """
        Creates a dataframe of each node's MO_name and distance from root
        """
        graph = self.network

        # root node id
        root_id = graph.nodes[0]["id"]

        # columns for dataframe
        tickers = []
        time_series_names = []
        distances_to_root = []
        is_driver_col = []
        for node in graph.nodes:
            tickers.append(node["ticker"])
            time_series_names.append(node["time_series_name"])
            distances_to_root.append(self.path_distances[root_id][node["id"]])
            is_driver_col.append(node["is_driver"])

        node_df = pd.DataFrame(
            {
                "ticker": tickers,
                "time_series_name": time_series_names,
                "distance_to_root": distances_to_root,
                "is_driver": is_driver_col,
            }
        )

        return node_df

    def list_time_series(self, search=""):
        """
        Lists out all the nodes
        """
        list_out = []
        if self.nodes:
            for node in self.nodes:
                if re.match(f".*{search}.*", node["title"]):
                    list_out.append(node["title"].split(":")[0])
        return list_out

    def time_series_names(self, search=""):
        """
        (Obsolete) Lists out all the nodes

        This method is kept for backwards-compatibility. New code should use list_time_series instead.
        """
        list_out = []
        if self.nodes:
            for node in self.nodes:
                if re.match(f".*{search}.*", node["title"]):
                    list_out.append(node["title"].split(":")[0])
        return list_out

    def create_time_series_chart(self, time_series_name):
        """
        Create a chart of given time series
        """
        # get needed data from dataframe
        df = self.df[self.df["time_series_name"] == time_series_name]

        if df.shape[0] == 0:
            print("Time series not found")
            return None

        df = df[df["period_name"].str.contains("Q")].sort_values("period_end_date")
        # use subset=['value'] to only drop rows with a null value
        df = df.dropna(subset=["value"])
        # NEED TO ACCOUNT FOR EMPTY DATAFRAMES
        row1 = df.iloc[0]
        title = row1["time_series_description"]
        xlabel = "Fiscal Quarter"
        ylabel = row1["time_series_description"]
        # plot data
        fig = px.line(
            df,
            x="period_name",
            y="value",
            title=title,
            labels={"period_name": xlabel, "value": ylabel},
        )
        return fig

    def show_time_series_chart(self, time_series_name):
        """
        Shows a chart of the given time series
        """
        fig = self.create_time_series_chart(time_series_name)
        fig.show()
        return


class Model:
    # functions which are CamelCase will become Classes at some point
    def __init__(
        self,
        ticker,
        config: Config = None,
        force=False,
        extract_drivers=True,
        historical_only=False,
        model_name=False,
        company_info=True,
    ):
        self.model_name = model_name
        self.config = config or CONFIG
        self.historical_only = historical_only
        self.ticker = ticker
        self.force = force
        self.company_info = company_info
        self.extract_drivers = extract_drivers

        self.api_headers = get_api_headers(self.config.canalyst_api_key)
        self.gt = Getter(self.config)

        self.set_new_uuid()
        self.scenario_url_map: Dict[str, str] = {}

        if self.force == True:
            print("model_frame")

        if self.company_info == True:
            # try:
            self.csin, self.latest_version = get_company_info_from_ticker(
                self.ticker, self.api_headers, self.config.mds_host
            )
            # except:
            #    print("Canalyst-Candas: Error on API Key.  Perhaps missing key.")

        self.get_model_frame()

        if self.extract_drivers == True:
            self.apply_drivers(self.force)

        if self.force == True:
            print("model_drivers")

        if self.extract_drivers == True:
            try:
                self._revenue_drivers = dot_parse(
                    self.default_df,
                    ticker=self.ticker,
                    auth_headers=self.api_headers,
                    config=self.config,
                    s3_client=self.gt,
                )
            except:
                self._revenue_drivers = None

        if self.force == True:
            print("guidance")
            self.create_guidance_csv()

        if self.model_name == True:
            self._model_name = self.get_excel_model_name()
            self._model_frame["model_name"] = self._model_name

    def plot_guidance(self, time_series_name):
        df_guidance = self.guidance()
        df_guidance["time_series_name"] = time_series_name
        df_guidance["period_name"] = df_guidance["Fiscal Period"]
        df_guidance["Actual"] = df_guidance["Output"]
        df_guidance = df_guidance[df_guidance["Item Name"] == time_series_name][
            [
                "time_series_name",
                "period_name",
                "Low",
                "High",
                "Mid",
                "Type.1",
                "Actual",
            ]
        ]
        df_guidance = (
            df_guidance.groupby(["time_series_name", "period_name"])
            .first()
            .reset_index()
        )

        i_low = df_guidance["Low"].sum()
        i_mid = df_guidance["Mid"].sum()
        i_high = df_guidance["High"].sum()

        if len({i_low, i_mid, i_high}) == 1:
            i_three = True
        else:
            i_three = False

        colors = {
            "red": "#ff207c",
            "grey": "#C3C2C3",
            "blue": "#00838F",
            "orange": "#ffa320",
            "green": "#00ec8b",
        }

        plt.rc("figure", figsize=(12, 9))
        plt.title(time_series_name)
        plt.plot(
            df_guidance["period_name"],
            df_guidance["Actual"],
            label="Actual",
            color=colors["blue"],
            linewidth=2,
        )
        plt.plot(
            df_guidance["period_name"],
            df_guidance["Mid"],
            label="Mid",
            color=colors["orange"],
            linewidth=2,
        )

        if i_three == False:
            plt.plot(
                df_guidance["period_name"],
                df_guidance["Low"],
                label="Low",
                color=colors["red"],
                linewidth=2,
            )
            plt.plot(
                df_guidance["period_name"],
                df_guidance["High"],
                label="High",
                color=colors["green"],
                linewidth=2,
            )

        plt.legend()
        plt.show()
        return

    def get_most_recent_model_date(self):
        """
        Get published date for latest workbook model
        """
        csin = self.csin
        auth_headers = self.api_headers
        mds_host = self.config.mds_host
        wp_host = self.config.wp_host

        from python_graphql_client import GraphqlClient

        client = GraphqlClient(endpoint=f"{wp_host}/model-workbooks")

        # Create the query string and variables required for the request.
        query = """
        query driversWorksheetByCSIN($csin: ID!) {
            modelSeries(id: $csin) {
            latestModel {
                id
                name
                publishedAt
                variantsByDimensions(
                    driversWorksheets: [STANDARD_FCF],
                    periodOrder: [CHRONOLOGICAL],
                ) {
                id
                downloadUrl
                variantDimensions {
                    driversWorksheets
                    periodOrder
                }
                }
            }
            }
        }
        """
        variables = {"csin": csin}

        # Synchronous request
        data = client.execute(
            query=query, variables=variables, headers=auth_headers, verify=False
        )
        url = data["data"]["modelSeries"]["latestModel"]["variantsByDimensions"][0][
            "downloadUrl"
        ]
        file_ticker = self.ticker.split(" ")[0]
        date_name = data["data"]["modelSeries"]["latestModel"]["publishedAt"]
        date_name = date_name.split("T")[0]
        return date_name

    def get_excel_model_name(self):
        """
        Get the model workbook's file name
        """
        csin = self.csin
        auth_headers = self.api_headers
        mds_host = self.config.mds_host
        wp_host = self.config.wp_host

        from python_graphql_client import GraphqlClient

        client = GraphqlClient(endpoint=f"{wp_host}/model-workbooks")

        # Create the query string and variables required for the request.
        query = """
        query driversWorksheetByCSIN($csin: ID!) {
            modelSeries(id: $csin) {
            latestModel {
                id
                name
                publishedAt
                variantsByDimensions(
                    driversWorksheets: [STANDARD_FCF],
                    periodOrder: [CHRONOLOGICAL],
                ) {
                id
                downloadUrl
                variantDimensions {
                    driversWorksheets
                    periodOrder
                }
                }
            }
            }
        }
        """
        variables = {"csin": csin}

        # Synchronous request
        data = client.execute(
            query=query, variables=variables, headers=auth_headers, verify=False
        )
        url = data["data"]["modelSeries"]["latestModel"]["variantsByDimensions"][0][
            "downloadUrl"
        ]
        file_ticker = self.ticker.split(" ")[0]
        file_name = data["data"]["modelSeries"]["latestModel"]["name"]
        return file_name

    def key_driver_map(self, time_series_name):
        """
        Returns a dataframe of key drivers for the MRQ
        """
        # defaulting to MO_RIS_REV, but you could choose another time_series_name as a starting point like MO_RIS_EBIT
        model_map = self.create_model_map(
            time_series_name=time_series_name,
            col_for_labels="time_series_name",
            notebook=False,
        )

        # list all the nodes in the model map
        model_map_time_series_list = model_map.list_time_series()

        # make it a dataframe because I'm a reformed R user
        df = pd.DataFrame(model_map_time_series_list)

        # columns for joining
        df.columns = ["time_series_name"]
        df["ticker"] = self.ticker

        # create a model frame with only key drivers and just the most recent quarter
        df_drivers = self.model_frame(
            is_driver=True, period_duration_type="fiscal_quarter", mrq=True
        )
        # merge (inner join)
        df = pd.merge(
            df,
            df_drivers,
            how="inner",
            left_on=["ticker", "time_series_name"],
            right_on=["ticker", "time_series_name"],
        )

        return df

    def forecast_frame(
        self, time_series_name, n_periods, function_name="value", function_value=""
    ):
        df = self.model_frame(
            [time_series_name],
            period_duration_type="fiscal_quarter",
            is_historical=False,
            n_periods=n_periods,
        )

        if function_name != "value":
            d = FuncMusic()
            df["new_value"] = df.apply(
                lambda row: d.apply_function(
                    row["value"], modifier=function_name, argument=function_value
                ),
                axis=1,
            )
        else:
            df["new_value"] = function_value

        df = df[
            [
                "ticker",
                "period_name",
                "time_series_name",
                "value",
                "new_value",
                "period_end_date",
            ]
        ]

        return df

    def create_time_series_chart(self, time_series_name, historical=False):  # MODEL
        # get needed data from dataframe
        df = self._model_frame[
            self._model_frame["time_series_name"] == time_series_name
        ]
        if df.shape[0] == 0:
            print("Time series not found")
            return None

        if historical:
            df = df.loc[df["is_historical"] == historical]

        df = df[df["period_name"].str.contains("Q")].sort_values("period_end_date")
        # use subset=['value'] to only drop rows with a null value
        df = df.dropna(subset=["value"])
        # NEED TO ACCOUNT FOR EMPTY DATAFRAMES
        row1 = df.iloc[0]
        title = self.ticker + " " + row1["time_series_description"]
        xlabel = "Fiscal Quarter"
        ylabel = row1["time_series_description"]

        colors = {
            "red": "#ff207c",
            "grey": "#C3C2C3",
            "blue": "#00838F",
            "orange": "#ffa320",
            "green": "#00ec8b",
        }

        plt.rc("figure", figsize=(12, 9))
        plt.title(time_series_name)
        plt.plot(
            df["period_name"],
            df["value"],
            label=ylabel,
            color=colors["blue"],
            linewidth=2,
        )
        plt.axvline(x=self.mrq()["period_name"][0], color="black")
        plt.xticks(rotation=90)
        plt.legend()
        plt.show()

        return

    def create_model_map(
        self,
        time_series_name="MO_RIS_REV",
        col_for_labels="time_series_name",
        tree=True,
        notebook=False,
        common_time_series_names=None,
    ):
        """
        Create a model map from this model, rooted at the specified time series

        Defaults to a model map rooted at MO_RIS_REV if no time series name is provided
        """
        mm = ModelMap(
            config=self.config,
            model=self,
            time_series_name=time_series_name,
            col_for_labels=col_for_labels,
            tree=tree,
            notebook=notebook,
            common_time_series=common_time_series_names,
        )
        self.model_map = mm
        return mm

    def get_params(self, search_term=""):
        df = self.default_df
        if search_term != "":
            search_term = "(?i)" + search_term
            df1 = df[df["time_series_description"].str.contains(search_term)]
            df2 = df[df["time_series_name"].str.contains(search_term)]
            df = pd.concat([df1, df2])
            df = (
                df.groupby(["time_series_name", "time_series_description"])
                .first()
                .reset_index()
            )
        df = df.sort_values("time_series_name")
        return df[["time_series_name", "time_series_description"]]

    def set_params(self, list_params=[]):
        self.set_new_uuid()
        scenario_name = self.uuid
        list_changes = []
        for param in list_params:
            list_changes.append(
                {
                    "time_series": param["feature_name"],
                    "period": param["feature_period"],
                    "value_expression": {
                        "type": "literal",
                        "value": param["feature_value"],
                    },
                }
            )

        data = {"changes": list_changes, "name": scenario_name}

        response = send_scenario(
            self.ticker,
            data,
            self.api_headers,
            self.csin,
            self.latest_version,
            self.config.mds_host,
        )

        self.record_scenario_url(response)

        return

    def show_model_map(
        self,
        time_series="MO_RIS_REV",
        tree=True,
        notebook=True,
        common_time_series=None,
    ):
        """
        Display model_map
        """
        mm = ModelMap(
            config=self.config,
            model=self,
            time_series_name=time_series,
            tree=tree,
            notebook=notebook,
            common_time_series=self._common_time_series_names,
        )
        self.model_map = mm
        return mm.show()

    def create_guidance_csv(self):
        """
        Write a CSV file containing the model's guidance data

        Parses guidance from the model's Excel workbook
        """
        file_ticker = self.ticker.split(" ")[0]
        path_name = f"{self.config.default_dir}/DATA/{file_ticker}/"
        os.makedirs(path_name, exist_ok=True)

        files = os.listdir(path_name)

        for filename in files:

            if "xlsx" in str(filename):
                try:
                    print("read excel for guidance")
                    df = pd.read_excel(
                        open(f"{path_name}" + filename, "rb"),
                        index_col=False,
                        sheet_name="Guidance",
                        engine="openpyxl",
                    )
                except:
                    return
                try:
                    save_guidance_csv(df, self.ticker, path_name)
                    return
                except:
                    print("Save guidance csv error")

    def set_new_uuid(self):
        self.uuid = datetime.datetime.now()
        self.uuid = str(self.uuid).replace(" ", "_")
        self.uuid = self.uuid.replace(":", ".")
        self.uuid = self.uuid.replace("-", "_")

    def mrq(self):
        df = self._model_frame
        df = df[df["is_historical"] == True]
        df = df[~df["period_name"].str.contains("FY")]
        df = df.sort_values("period_end_date", ascending=False)
        return pd.DataFrame(
            df.iloc[0][["period_name", "period_end_date"]]
        ).T.reset_index()[["period_name", "period_end_date"]]

    def guidance(self):
        df = self.gt.get_file(self.ticker, "guidance")
        df = df.dropna()
        self._guidance = df
        return df

    def get_drivers(self, force=False):
        """
        Gets the associated list of drivers for the model.

        Supply with force=False to use cache.
        """
        df = self.gt.get_file(self.ticker, "model_drivers")

        if df is not None and force == False:
            self._model_drivers = df
            return

        drivers = get_drivers_from_api(
            self.config.mds_host, self.csin, self.latest_version, self.api_headers
        )

        df_new = pd.json_normalize(drivers)
        df_driver_array = pd.DataFrame(df_new["time_series.names"])
        df_drivers = df_driver_array.explode("time_series.names")
        df = df_drivers.groupby("time_series.names").first().reset_index()
        df.columns = ["time_series_name"]

        self._model_drivers = df

        ticker = self.ticker.split(" ")[0]

        self._model_drivers.to_csv(
            f"{self.config.default_dir}/DATA/{ticker}/{self.ticker}_model_drivers.csv",
            index=False,
        )

        self.get_name_index(force=self.force)

    def get_name_index(self, force=False):

        self.df_name_index = get_name_index_from_csv(self.ticker, self.config)

        ticker = self.ticker.split(" ")[0]

        self.df_name_index.to_csv(
            f"{self.config.default_dir}/DATA/{ticker}/{self.ticker}_name_index.csv",
            index=False,
        )
        return

    def revenue_drivers(self, search_term="", is_driver=False):
        pd.set_option("display.max_colwidth", None)
        df = self._model_frame
        df_only_drivers = self._revenue_drivers
        df = pd.merge(
            df,
            df_only_drivers,
            how="inner",
            left_on="time_series_name",
            right_on="time_series_name_dependent",
        )
        df1 = df[
            df["time_series_description"].str.contains(
                search_term, flags=re.IGNORECASE, regex=True
            )
        ]
        df2 = df[
            df["time_series_name"].str.contains(
                search_term, flags=re.IGNORECASE, regex=True
            )
        ]
        df = pd.concat([df1, df2])
        df = df.dropna()
        df = (
            df.groupby(["time_series_name", "time_series_description"])
            .first()
            .reset_index()
        )
        df = df.drop(
            columns=[
                "period_duration_type",
                "category_type_slug",
                "time_series_slug",
                "category_type_name",
                "category_slug",
                "is_historical",
                "value",
                "period_start_date",
                "period_end_date",
                "period_name",
                "time_series_name",
                "time_series_description",
            ]
        )
        df = df.sort_values("index")
        df = df.reset_index()
        df = df.drop(columns=["index", "level_0"])
        if is_driver == True:
            df = df.loc[df["is_driver"] == True]
            return df
        return df

    def model_drivers(self, search_term=""):
        mrq = self.mrq()["period_name"][0]
        df = self._model_drivers
        df2 = self._model_frame
        df2 = df2.loc[df2["period_name"] == mrq]
        df = pd.merge(
            df,
            df2,
            how="inner",
            left_on="time_series_name",
            right_on="time_series_name",
        )[
            ["name_index", "category", "time_series_name", "time_series_description"]
        ].sort_values(
            "name_index", ascending=True
        )

        if search_term != "":
            df = df[
                df["time_series_name"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
        return df

    # MODEL model_frame
    def model_frame(
        self,
        time_series_name="",
        period_name="",
        is_driver="",
        pivot=False,
        mrq=False,
        period_duration_type="",
        is_historical="",
        n_periods=12,
        mrq_notation=False,
        unit_type="",
        category="",
        warning=True,
        n_diff="",
    ):
        return filter_dataset(
            self._model_frame,
            time_series_name,
            period_name,
            is_driver,
            pivot,
            mrq,
            period_duration_type,
            is_historical,
            n_periods,
            mrq_notation,
            unit_type,
            category,
            warning,
        )

    def apply_drivers(self, force=False):

        # this is a separate step for debug... should merge into model_frame

        df = self.gt.get_file(self.ticker, "model_drivers")

        if df is not None and force == False:
            self._model_drivers = df
        else:
            print("get driver library")
            self.get_drivers(force=self.force)
            df = self._model_drivers

        df = df.assign(is_driver=True)
        df2 = pd.merge(
            self._model_frame,
            df,
            how="outer",
            left_on="time_series_name",
            right_on="time_series_name",
        )
        df2 = df2[df2["ticker"].notna()]
        df2[["is_driver"]] = df2[["is_driver"]].fillna(value=False)
        self._model_frame = df2

        df_index = get_data_set_from_mds(
            CsvDataKeys.NAME_INDEX,
            self.csin,
            self.latest_version,
            self.api_headers,
            self.log,
            settings.MDS_HOST,
        )

        if df_index is not None:
            df_index.columns = ["time_series_name", "name_index"]
        else:
            mrq = self._model_frame["MRQ"].loc[0]
            df_index = self._model_frame.loc[self._model_frame["period_name"] == mrq][
                ["time_series_name"]
            ]
            df_index["name_index"] = np.arange(len(df_index))

        self._model_frame = pd.merge(
            self._model_frame,
            df_index,
            how="outer",
            left_on="time_series_name",
            right_on="time_series_name",
        )

        self._model_frame = self._model_frame[self._model_frame["period_name"].notna()]
        return

    def get_model_frame(self):

        df_hist = self.historical_data_frame()
        df_hist = df_hist.assign(is_historical=True)
        df_hist = df_hist[~df_hist["period_name"].isna()]

        mrq = df_hist["period_name"].iloc[0]
        pd.options.mode.chained_assignment = None

        df_fwd = self.forward_data_frame()
        df_fwd = df_fwd.assign(is_historical=False)
        df_fwd = df_fwd[~df_fwd["period_name"].isna()]

        df_concat = pd.concat([df_hist, df_fwd]).sort_values("period_name")

        self._model_frame = df_concat

        mrq = self.mrq()["period_name"][0]
        self._model_frame["MRQ"] = [mrq for i in range(len(self._model_frame))]
        return

    def feature_search(self, search_term=""):
        if search_term != "":
            df = self._model_frame
            df1 = df[
                df["time_series_description"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df2 = df[
                df["time_series_name"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df = pd.concat([df1, df2])
            df = (
                df.groupby(["time_series_name", "time_series_description"])
                .first()
                .reset_index()
            )
            df = df[["time_series_name", "time_series_description"]]
        return df

    def driver_search(self, search_term=""):
        df = self._model_drivers
        if search_term != "":
            df = self._model_frame
            df_only_drivers = self._model_drivers
            df_drivers = pd.merge(
                df,
                df_only_drivers,
                how="inner",
                left_on="time_series_name",
                right_on="time_series_name",
            )
            df1 = df[
                df["time_series_description"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df2 = df[
                df["time_series_name"].str.contains(
                    search_term, flags=re.IGNORECASE, regex=True
                )
            ]
            df = pd.concat([df1, df2])
            df = (
                df.groupby(["time_series_name", "time_series_description"])
                .first()
                .reset_index()
            )
            df = df[["time_series_name", "time_series_description"]]
        return df

    def describe_drivers(self, filter_string=""):
        """
        Get a summary DataFrame of the model's drivers
        """
        # if self.describe_drivers is not None:
        #    return self.describe_drivers
        # get the historical dataframe from candas
        df = self.historical_data_frame()

        df_only_drivers = self._model_drivers
        # merge the drivers and the historical data... and return a description of the values for each
        df_drivers = pd.merge(
            df,
            df_only_drivers,
            how="inner",
            left_on="time_series_name",
            right_on="time_series_name",
        )
        df_drivers_summary = (
            df_drivers.groupby(["time_series_name"]).describe().reset_index()
        )
        if filter_string != "":
            self.describe_drivers = df_drivers_summary
            return df_drivers_summary[
                df_drivers_summary["time_series_name"].str.contains(
                    filter_string, case=False
                )
            ]
        self._describe_drivers = df_drivers_summary
        return df_drivers_summary

    def historical_data_frame(self):  # if cache = true save locally?
        """
        Get a DataFrame of the model's historical data
        """

        if self.force == False:
            df = get_data_set_from_mds(
                CsvDataKeys.HISTORICAL_DATA,
                self.csin,
                self.latest_version,
                self.api_headers,
                self.log,
                self.config.mds_host,
            )
            if df is not None:
                return df

        file_ticker = self.ticker.split(" ")[0]
        path_name = f"{self.config.default_dir}/DATA/{file_ticker}/"
        os.makedirs(path_name, exist_ok=True)

        try:
            url_hist, model_info = get_model_info(
                self.ticker,
                self.api_headers,
                self.config.default_dir,
                self.config.mds_host,
            )
        except:
            return

        crawl_args = {
            "next_url": url_hist,
            "ticker": self.ticker,
            "key_name": "results",
            "next_name": "next",
            "auth_headers": self.api_headers,
            "default_dir": self.config.default_dir,
        }

        crawl_company_pages(**crawl_args)

        dict_json = read_json(self.ticker, self.config.default_dir)

        df = json_to_df(dict_json, self.ticker)

        df.to_csv(path_name + self.ticker + "_historical_data.csv")
        df_model_info = pd.DataFrame(model_info)
        df_model_info.to_csv(path_name + self.ticker + "_model_info.csv")

        # Converts the "value" column from an object type to a float64 type
        df["value"] = pd.to_numeric(df["value"])
        return df

    def summary(self, filter_term=""):
        pd.set_option("mode.chained_assignment", None)
        pd.set_option("display.float_format", lambda x: "%.5f" % x)

        df = pd.merge(
            self.model_frame(
                period_duration_type="fiscal_quarter",
                is_historical=False,
                warning=False,
            ),
            self.scenario_df,
            how="inner",
            left_on=[
                "ticker",
                "period_name",
                "time_series_name",
                "time_series_description",
            ],
            right_on=[
                "ticker",
                "period_name",
                "time_series_name",
                "time_series_description",
            ],
        )[
            [
                "ticker",
                "period_name",
                "time_series_name",
                "time_series_description",
                "value_x",
                "value_y",
            ]
        ]
        df.columns = [
            "ticker",
            "period_name",
            "time_series_name",
            "time_series_description",
            "default",
            "scenario",
        ]
        df["diff"] = df["scenario"].astype(float) / df["default"].astype(float)
        if filter_term != "":
            df = df[df["time_series_name"].str.contains(filter_term, case=False)]
        return df

    def forward_data_frame(self):
        if self.force == False:
            df = get_data_set_from_mds(
                CsvDataKeys.FORECAST_DATA,
                self.csin,
                self.latest_version,
                self.api_headers,
                self.log,
                self.config.mds_host,
            )
            if df is not None:
                self.default_df = df
                return df

        file_ticker = self.ticker.split(" ")[0]
        path_name = f"{self.config.default_dir}/DATA/{file_ticker}/"
        file_name = f"{path_name}{self.ticker}_forecast_data.csv"

        if not os.path.exists(path_name):
            os.makedirs(path_name)

        if self.csin == "":
            self.csin, self.latest_version = get_company_info_from_ticker(
                self.ticker, self.api_headers, self.config.mds_host
            )

        url = get_forecast_url(self.csin, self.latest_version, self.config.mds_host)

        res = get_request(url, self.api_headers)

        list_out = []

        for res_dict in res.json()["results"]:
            df = get_forecast_url_data(res_dict, self.ticker, self.api_headers)
            list_out.append(df)

        self.default_df = pd.concat(list_out)
        self.default_df.to_csv(file_name, index=False)

        return df

    def model_fit(self, time_series_name=""):

        if self.csin == "":
            self.csin, self.latest_version = get_company_info_from_ticker(
                self.ticker,
                auth_headers=self.api_headers,
                mds_host=self.config.mds_host,
            )

        url = get_forecast_url(self.csin, self.latest_version, self.config.mds_host)

        scenario_url = (
            f"{self.config.mds_host}/"
            f"{SCENARIO_URL.format(csin=self.csin, version=self.latest_version)}"
        ) + "?page_size=200"

        if self.scenario_url_map.get(self.uuid) is None:
            scenario_response = get_request(scenario_url, headers=self.api_headers)
            scenario_json = scenario_response.json()
            scenario_id_url = map_scenario_urls(scenario_json).get(self.uuid)
        else:
            scenario_id_url = self.scenario_url_map[self.uuid]

        if scenario_id_url is None:

            print("Scenario ID for " + scenario_url + " is None.")

            return

        print(self.ticker + " scenario_id_url: " + str(scenario_id_url))

        if time_series_name != "":

            url = scenario_id_url + "time-series/?name=" + time_series_name

            res_loop = get_request(url, self.api_headers)
            url = res_loop.json()["results"][0]["self"]
            res_loop = get_request(url, self.api_headers)
            url = res_loop.json()["forecast_data_points"]
            res_loop = get_request(url, self.api_headers)
            res_data = res_loop.json()["results"]
            dict_out = {}
            list_out = []
            for res_data_dict in res_data:
                dict_out["time_series_slug"] = res_data_dict["time_series"]["slug"]
                dict_out["time_series_name"] = res_data_dict["time_series"]["names"][0]
                dict_out["time_series_description"] = res_data_dict["time_series"][
                    "description"
                ]
                dict_out["category_slug"] = res_data_dict["time_series"]["category"][
                    "slug"
                ]
                dict_out["category_type_slug"] = res_data_dict["time_series"][
                    "category"
                ]["type"]["slug"]
                dict_out["category_type_name"] = res_data_dict["time_series"][
                    "category"
                ]["type"]["name"]
                dict_out["unit_description"] = res_data_dict["time_series"]["unit"][
                    "description"
                ]
                dict_out["unit_symbol"] = res_data_dict["time_series"]["unit"]["symbol"]
                dict_out["period_name"] = res_data_dict["period"]["name"]
                dict_out["period_duration_type"] = res_data_dict["period"][
                    "period_duration_type"
                ]
                dict_out["period_start_date"] = res_data_dict["period"]["start_date"]
                dict_out["period_end_date"] = res_data_dict["period"]["end_date"]
                dict_out["value"] = res_data_dict["value"]
                dict_out["ticker"] = self.ticker
                df = pd.DataFrame.from_dict(dict_out, orient="index").T
                list_out.append(df)
            self.scenario_df = pd.concat(list_out)
            return

        scenario_id_url = scenario_id_url + "forecast-periods/"

        scenario_response = get_request(scenario_id_url, headers=self.api_headers)
        all_df = []

        all_df = Parallel(n_jobs=num_cores)(
            delayed(get_scenario_url_data)(res_dict, self.ticker)
            for res_dict in scenario_response.json()["results"]
        )
        self.scenario_df = pd.concat(all_df)
        print("Done")
        return

    def record_scenario_url(self, scenario_response: Response) -> None:
        if scenario_response is None:
            return None
        """
        Extract scenario name and location from the response and add to scenario url dictionary
        """
        scenario_name = self.uuid
        scenario_url = scenario_response.headers["Location"]

        if self.scenario_url_map.get(scenario_name) is None:
            self.scenario_url_map[scenario_name] = scenario_url


class Chart:
    """
    Charting class to create consistent and branded charts
    ...

    Attributes
    ----------
    x_value : pd.Series
        the data for the x-axis
    y_values : pd.Dataframe
        the data for the y-axis
    labels : list
        a list of strings to specify labels of y_value columns respectively (Default: None)
    axis_labels : list
        a list of tuples of strings to specify x,y axis labels (Default: None)
    title : str
        the title of the chart (Default: None)
    plot_styles : list
        list of chart styles for y-value columns (can specify only 1 style to apply to all columns) (Default: ["line"])
    use_subplots : bool
        bool to indicate if subplots should be used (i.e chart columns on the same graph or not) (Default: False)
    subplot_scale_width : list
        list of ints to specify width scaling for subplots (length of list must match # of subplots) (Default: None)
    subplot_scale_height : list
        list of ints to specify height scaling for subplots (length of list must match # of subplots) (Default: None)
    figure_size : tuple
        tuple to define figure size (Default: (12,9))
    vertical_line : str or pd.Series
        str or dataframe series to define where to place a vertical line on the graph on the x-axis (Default: None)
    marker : str
        str to define marker type (Default: "o")
    markersize : int
        the size of markers (Default: 8)
    markevery : int or float
        int argument will define plotting of every nth marker from the first data point.  (Default: None)
    plot_config : dict
        extra arguments to be passed into the .plot() command. Arguments must be valid for the plot style being used. (Default: None)
    xtick_rotation : int
        specifies the rotation of x-axis tick labels (Default: 90)
    display_charts_horizontal : bool
        specifies if subplots should be displayed horizontally instead of vertically (Default: False)
    subplot_adjustment : list
        list in the form of [left, bottom, right, top] to tune subplot layout. (Default: [0.125, 0.2, 0.9, 0.9])

    Methods
    -------
    show()
        Displays the graph generated

    """

    def __init__(
        self,
        x_value,
        y_values,
        labels=None,
        axis_labels=None,
        title="",
        plot_styles=[
            "line"
        ],  # If only 1 style defined, it will be applied to all columns
        use_subplots=False,
        subplot_scale_width=None,
        subplot_scale_height=None,
        figure_size=(12, 9),
        vertical_line=None,
        marker="o",
        markersize=8,
        markevery=None,
        plot_config={},
        xtick_rotation=90,
        display_charts_horizontal=False,
        subplot_adjustment=[0.125, 0.2, 0.9, 0.9],
    ):

        self.x_value = x_value
        self.y_values = y_values
        self.labels = labels
        self.axis_labels = axis_labels
        self.title = title
        self.use_subplots = use_subplots
        self.plot_styles = plot_styles
        self.subplot_scale_width = subplot_scale_width
        self.subplot_scale_height = subplot_scale_height
        self.figure_size = figure_size
        self.vertical_line = vertical_line
        self.markevery = markevery
        self.marker = marker
        self.markersize = markersize
        self.plt_plot_style = "fivethirtyeight"
        self.plot_config = plot_config
        self.xtick_rotation = xtick_rotation
        self.display_charts_horizontal = display_charts_horizontal
        self.subplot_adjustment = subplot_adjustment
        self.canalyst_colors = {
            "cloud-grey": "#E2E3E3",
            "yellow": "#FFD200",
            "teal": "#00838F",
            "red": "#E52B26",
            "grey": "#C3C2C3",
            "blue": "#00838F",
            "orange": "#F8623F",
            "green": "#30C08F",
        }

        self._validate_args()
        self.main_fpath = Path("canalyst_candas/fonts/Barlow-SemiBold.ttf")
        self.secondary_fpath = Path("canalyst_candas/fonts/Roboto-Regular.ttf")

        self.fig, self.axs = self.build_chart()

    def _validate_args(self):
        """
        Validate arguments used in initialization
        """
        if not type(self.plot_styles) == list:
            print(
                "Plot styles must be specified in the form of a list. Please re-instantiate the "
                'object with plot style in the form of "["plot_style_here"]". Available options '
                'are "line", "bar", "barh", "scatter".'
            )
        if not type(self.labels) == list:
            print(
                "Labels must be specified in the form of a list. Please re-instantiate the object"
                'with labels in the form of "["Label", "Label"]" depending on how many columns'
                "are being passed in."
            )

        if isinstance(self.y_values, pd.DataFrame):
            if type(self.labels) == list and not len(self.labels) == len(
                self.y_values.columns
            ):
                print("Warning: Labels have not been appointed for all columns.")

        if isinstance(self.y_values, pd.Series):
            if type(self.plot_styles) == list and len(self.plot_styles) > 1:
                print(
                    "Only 1 plot style needed for the specified y data. Only the first value "
                    "in the list will be used."
                )
        elif isinstance(self.y_values, pd.DataFrame):
            columns = len(self.y_values.columns)
            # If user has specified only 1 plot style for multiple columns, extend it to all columns
            if type(self.plot_styles) == list and len(self.plot_styles) == 1:
                self.plot_styles = self.plot_styles * columns
            elif (
                not type(self.plot_styles) == list
                or not len(self.plot_styles) == columns
            ):
                print(
                    "Please explictly specify the plot style of all Y value columns in a list "
                    "or 1 style to be applied for all."
                )

    def _add_watermark(self, ax):
        """
        Adds a Canalyst Logo to the top left corner of the graph
        """

        logo = image.imread(os.getcwd() + "/canalyst_candas/images/logo.png")
        starting_x, starting_y, width, height = ax.get_position().bounds

        # Units seem to be in inches:
        # https://matplotlib.org/devdocs/gallery/subplots_axes_and_figures/figure_size_units.html#:~:text=The%20native%20figure%20size%20unit,units%20like%20centimeters%20or%20pixels.
        logo_width = 0.06
        logo_height = 0.06

        # Change the numbers in this array to position your image [left, bottom, width, height])
        ax = plt.axes(
            [
                starting_x + 0.01,
                starting_y + height - logo_height,
                logo_width,
                logo_height,
            ],
            frameon=True,
        )
        ax.imshow(logo)
        ax.axis("off")

    def setup_basic_chart_options(self, fig):
        """
        Sets up figure with basic chart options
        """
        plt.rc("figure", figsize=self.figure_size)
        plt.style.use(self.plt_plot_style)
        fig.patch.set_facecolor("#fff")

        # Adjust subplot chart display positions
        left, bottom, right, top = self.subplot_adjustment
        plt.subplots_adjust(left, bottom, right, top)

    def build_chart(self, force=False):
        """
        Builds a matplotlib chart. Returns figure and ax(s).
        """

        # Avoid rebuilding if not required
        try:
            if self.fig and self.axs and force is False:
                return self.fig, self.axs
        except AttributeError:
            pass

        if isinstance(self.y_values, pd.Series):
            fig, ax = self._get_chart_without_subplots(is_series=True)
        elif isinstance(self.y_values, pd.DataFrame):
            if not self.use_subplots:
                fig, ax = self._get_chart_without_subplots(is_series=False)
            else:
                # Use subplots
                fig, ax = self._get_chart_with_subplots()

        # If a vertical line is specified, and there are subplots: apply it on all subplots
        # If not, apply it to just the one graph.
        if self.vertical_line:
            color = self.canalyst_colors["cloud-grey"]
            if type(ax) == np.ndarray:
                for index, item in enumerate(ax):
                    ax[index].axvline(x=self.vertical_line, color=color)
            else:
                ax.axvline(x=self.vertical_line, color=color, linewidth=2)

        return fig, ax

    def _get_axis_label(self, index):
        """
        Return axis label at position specified.

        Returns None if class not initialized with axis_labels.
        """
        if self.axis_labels is not None:
            try:
                return self.axis_labels[index]
            except IndexError:
                pass

        return None

    def _get_label(self, index):
        """
        Return label at position specified.

        Returns None if class not initialized with labels.
        """
        if self.labels is not None:
            try:
                return self.labels[index]
            except IndexError:
                pass
        return None

    def _get_chart_without_subplots(self, is_series=True):
        """
        Returns figure and ax for charts without subplots for series or dataframes
        """
        fig, ax = plt.subplots()
        first_element = 0

        # Get and set custom font
        fig.suptitle(
            self.title, font=self.main_fpath, size="x-large", weight="bold", y=0.96
        )

        self.setup_basic_chart_options(fig)

        label = self._get_label(first_element)
        axis_label = self._get_axis_label(first_element)

        # If series is specified, we only have 1 y-value to graph
        if is_series:
            self._set_graph_ax(
                ax,
                self.plot_styles[0],
                self.x_value,
                self.y_values,
                label,
                axis_label,
                "cloud-grey",
                self.marker,
                self.markersize,
                self.markevery,
            )
        else:
            # Want to graph multiple y-values on the same graph
            color_options = [
                "cloud-grey",
                "yellow",
                "teal",
                "blue",
                "red",
                "green",
                "orange",
            ]

            for index, column in enumerate(self.y_values):
                label = self._get_label(index)
                self._set_graph_ax(
                    ax,
                    self.plot_styles[index],
                    self.x_value,
                    self.y_values[column],
                    label,
                    axis_label,
                    color_options[
                        index % 7
                    ],  # Use index modded by length of color_options to select unique colors, up to 7, then colors repeat.
                    self.marker,
                    self.markersize,
                    self.markevery,
                )

        self._format_graph(ax, fig)
        return fig, ax

    def _get_scale_arguments(self):
        """
        Return width, height scale arguments, if any
        """
        scale_args = {}

        if self.subplot_scale_width and self.subplot_scale_height:
            scale_args = {
                "gridspec_kw": {
                    "width_ratios": self.subplot_scale_width,
                    "height_ratios": self.subplot_scale_height,
                }
            }
        elif self.subplot_scale_width:
            scale_args = {"gridspec_kw": {"width_ratios": self.subplot_scale_width}}
        elif self.subplot_scale_height:
            scale_args = {"gridspec_kw": {"height_ratios": self.subplot_scale_height}}

        return scale_args

    def _get_chart_with_subplots(self):
        """
        Returns figure and ax for charts with subplots for dataframes
        """
        color_options = [
            "cloud-grey",
            "yellow",
            "teal",
            "blue",
            "red",
            "green",
            "orange",
        ]
        columns = len(self.y_values.columns)
        scale_args = self._get_scale_arguments()

        # If specified, display subplots horizontally
        if columns % 2 == 0 and self.display_charts_horizontal:
            row = int(columns / 2)
            row_column = {"nrows": row, "ncols": columns}
        else:
            row_column = {"nrows": columns}

        fig, axs = plt.subplots(
            **row_column,
            **scale_args,
            sharex=True,
        )

        # Set custom Font and figure title
        fig.suptitle(
            self.title, font=self.main_fpath, size="x-large", weight="bold", y=0.96
        )

        self.setup_basic_chart_options(fig)

        # Plot each column from the Y-column dataset provided
        for index, column in enumerate(self.y_values):
            label = self._get_label(index)
            axis_label = self._get_axis_label(index)

            self._set_graph_ax(
                axs[index],
                self.plot_styles[index],
                self.x_value,
                self.y_values[column],
                label,
                axis_label,
                color_options[index % 4],
                self.marker,
                self.markersize,
                self.markevery,
            )
            self._format_graph(axs[index], fig)

        return fig, axs

    def _set_graph_ax(
        self,
        ax,
        plot_style,
        x_value,
        y_value,
        label,
        axis_labels,
        color,
        marker,
        markersize,
        markevery,
    ):
        """
        Builds a matplotlib chart on the ax provided based on configurations specified.
        """
        # Set up axis labels
        if axis_labels is not None:
            x_label, y_label = axis_labels
            ax.set_xlabel(x_label, font=self.main_fpath, labelpad=15)
            ax.set_ylabel(y_label, font=self.main_fpath, labelpad=15)

        # Plot the type of bar specified
        if plot_style == "bar":
            ax.bar(
                x_value,
                y_value,
                label=label,
                color=self.canalyst_colors[color],
                width=0.4,
                zorder=-1,
                **self.plot_config,
            )
        elif plot_style == "scatter":
            ax.scatter(
                x_value,
                y_value,
                label=label,
                color=self.canalyst_colors[color],
                zorder=3,
            )
        elif plot_style == "barh":
            ax.barh(
                x_value,
                y_value,
                label=label,
                color=self.canalyst_colors[color],
                zorder=-2,
                **self.plot_config,
            )
        else:  # line graph or catch all
            ax.plot(
                x_value,
                y_value,
                label=label,
                color=self.canalyst_colors[color],
                marker=marker,
                markersize=markersize,
                markevery=markevery,
                linewidth=2,
                zorder=1,
                **self.plot_config,
            )

    def _format_graph(self, ax, fig):
        """
        Formats ax's
        """
        # General grid and chart options
        ax.grid(linewidth=0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(self.canalyst_colors["grey"])
        ax.spines["bottom"].set_color(self.canalyst_colors["grey"])
        ax.set_facecolor("#161B21")

        # Setup Legend
        columns = 1
        if isinstance(self.y_values, pd.DataFrame):
            columns = len(self.y_values.columns)

        # Set custom Font
        font_name = fm.FontProperties(fname=self.secondary_fpath)

        fig.legend(
            loc="lower left",
            bbox_to_anchor=(0.1, 0),
            fancybox=True,
            shadow=True,
            ncol=columns,
            frameon=False,
            prop=font_name,
        )

        # Set up x,y axis tick labels
        config_ticks = {
            "size": 0,
            "labelcolor": "black",
            "labelsize": 12,
            "pad": 10,
        }
        ax.tick_params(axis="both", **config_ticks)

        # Add Canalyst watermark
        self._add_watermark(ax)

        for tick in ax.get_xticklabels():
            tick.set_font(self.secondary_fpath)
        for tick in ax.get_yticklabels():
            tick.set_font(self.secondary_fpath)

        # Set the rotation for tick labels
        for tick in ax.get_xticklabels():
            tick.set_rotation(self.xtick_rotation)

    def show(self):
        """
        Displays Chart
        """
        plt.show()
