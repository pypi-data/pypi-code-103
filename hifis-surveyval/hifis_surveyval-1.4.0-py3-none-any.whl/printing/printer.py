# hifis-surveyval
# Framework to help developing analysis scripts for the HIFIS Software survey.
#
# SPDX-FileCopyrightText: 2021 HIFIS Software <support@hifis.net>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
This module provides a framework for printing.

.. currentmodule:: hifis_surveyval.printing.printer
.. moduleauthor:: HIFIS Software <software@hifis.net>
"""

from pprint import PrettyPrinter
from typing import Dict, List, Union

import click
import pandas
from tabulate import tabulate


class Printer:
    """Class providing printing functionality."""

    @classmethod
    def pretty_print(cls, to_print: Union[List, Dict]) -> None:
        """
        Print a list or dictionary with pprint.

        Args:
            to_print (Union[List, Dict]): Data to be printed by PrettyPrint.
        """
        pp = PrettyPrinter(indent=4)
        pp.pprint(to_print)

    @classmethod
    def print_table(
        cls, table: List[Union[List, Dict]], table_headers: List
    ) -> None:
        """
        Print a list of lists as ascii table.

        The lists in the table list need to have the same size as the list for
        the headers. Every list in the able list is a row in the output.

        Args:
            table (List[Union[List, Dict]]): Table body to be printed.
            table_headers (List): Table header to be printed.

        Raises:
            ValueError: Exception thrown if header and body lengths differ.
        """
        header_length = len(table_headers)
        for row in table:
            if len(row) != header_length:
                raise ValueError(
                    "Not all table rows are as long as the header."
                )
        click.echo(click.style(tabulate(table, headers=table_headers)))

    @classmethod
    def print_dataframe(cls, data_frame: pandas.DataFrame):
        """
        Print a pandas dataframe.

        Args:
            data_frame(pandas.DataFrame): Pandas DataFrame to be printed.
        """
        print(data_frame)
