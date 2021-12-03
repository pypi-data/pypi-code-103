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

"""This module provides helper functions."""
import os
import shutil
from pathlib import Path
from typing import Any, List, Optional

from pandas import DataFrame, Series, concat

from hifis_surveyval.core.settings import Settings


def dataframe_value_counts(
    dataframe: DataFrame,
    relative_values: bool = False,
    drop_nans: bool = True,
) -> DataFrame:
    """
    Count how often a unique value appears in each column of a data frame.

    Args:
        dataframe (DataFrame):
            The data frame of which the values shall be counted.
        relative_values (bool):
            Instead of absolute counts fill the cells with their relative
            contribution to the column total
        drop_nans (bool):
            Whether to remove the NaN value count. Defaults to True
    Returns:
        DataFrame:
            A new data frame with the same columns as the input. The index is
            changed to represent the unique values and the cells contain the
            count of the unique values in the given column.
    """
    new_frame: DataFrame = DataFrame(
        [
            dataframe[column].value_counts(
                normalize=relative_values, dropna=drop_nans
            )
            for column in dataframe.columns
        ]
    )
    new_frame.fillna(0, inplace=True)
    new_frame = new_frame.transpose()

    return new_frame


def cross_reference_sum(data: DataFrame, grouping: Series) -> DataFrame:
    """
    Cross references a data frame with a series and count correlations.

    The data frame is processed column-wise.
    For each column, indices are grouped up by their respective value in the
    grouping series and each group is summed up.

    Columns with incomplete data or rows that can not be cross-referenced may
    be dropped.

    In the context of the survey analysis, data usually is a multiple choice
    question, while the grouping series is a single choice question.
    They get matched by the participant IDs and the correlations get summed up.

    Args:
        data (DataFrame):
            A data frame of which the columns are to be grouped and summed up.
        grouping (Series):
            A series with indices (mostly) matching that of "data", associating
            each index with a group towards which the values of "data" are to
            be counted.
    Returns:
        DataFrame:
            A data frame containing the columns from data (minus dropped
            columns) and the unique values of the grouping series as indices.
            Each cell at [column, index] holds the sum of the values in the
            respective column of the data which corresponded to the index in
            the grouping series.
    """
    grouping_values: List[Any] = grouping.unique()
    grouping_header: str = str(grouping.name)

    # Join the frame and the series for association and clean N/A values
    # Rows that can not be associated get dropped, they will not contribute to
    # the summary.
    joined_frame: DataFrame = data.join(grouping, how="inner")
    joined_frame.dropna(inplace=True)

    # Process the singular rows and keep them in a list to concatenate them all
    # at once later on. This seems to be more efficient than DataFrame.append()
    # The latter also seems to drop the type information which can lead to
    # trouble when attempting to plot the result.
    per_field: List[Series] = []
    for current_group in grouping_values:
        mask = joined_frame[grouping_header] == current_group
        filtered = joined_frame[mask]

        # Drop the series entries previously added for association, so they do
        # not show up in the result. Also set the name so it becomes the index
        # label on concatenation.
        summary: Series = filtered.drop(columns=[grouping_header]).sum()
        summary.name = current_group
        per_field.append(summary)

    return concat(per_field, axis=1)


# TODO Remove filter and group for Questions?
def filter_and_group_series(
    base_data: Series,
    group_by: Series,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
) -> DataFrame:
    """
    Filter a series and group its values according to another series.

    Generate a sparse DataFrame in which all values of base_data are assigned
    to a column according to the corresponding value for the same index in
    group_by.

    Indexes not present in group_by will result in an empty row.
    Indexes not present in base_data will result in an empty column.

    Args:
        base_data (Series):
            The series of which the data is to be sorted and filtered.
        group_by (Series):
            A series assigning each index to a group.
        min_value (Optional[float]):
            An optional minimum value. All values of base_data below this
            value will be excluded from the result. Not set by default.
        max_value (Optional[float]):
            An optional maximum value. All values of base_data above this
            value will be excluded from the result. Not set by default.
    Returns:
        DataFrame:
            A new DataFrame where each row represents an index of base_data
            and each column is one of the unique values of the group_by series.
            The values of base_data are put into the column where the base_data
            index matches the group_by index.
    """
    if group_by.isna().values.any():
        raise ValueError("The group-by series contains NaN values. Please "
                         "drop NaN values from the group-by series before "
                         "passing it as an argument.")

    result_frame: DataFrame = DataFrame(
        index=base_data.index, columns=group_by.unique()
    )

    for group_index, group_name in group_by.iteritems():
        if group_index not in base_data.index:
            continue
        value = base_data.get(group_index, None)

        # Apply all the filters
        if max_value and max_value < value:
            continue

        if min_value and min_value > value:
            continue

        result_frame[group_name][group_index] = value

    return result_frame


def create_example_script(settings: Settings) -> None:
    """
    Create an example script from data payload at the default script location.

    Args:
        settings (Settings):
            Settings of the analysis run.
    """
    # create folder to store the scripts
    if settings.SCRIPT_FOLDER is not None:
        if not settings.SCRIPT_FOLDER.exists():
            settings.SCRIPT_FOLDER.mkdir(parents=True)

    # copy a file from the packages file payload to the set up scripts folder
    shutil.copy(
        f"{Path(__file__).parent.parent.absolute()}/files/example_script.py",
        settings.SCRIPT_FOLDER.resolve(),
    )


def create_preprocessing_script(settings: Settings) -> None:
    """
    Create an empty preprocessing script at the default location.

    Args:
        settings (Settings):
            Settings of the analysis run.
    """
    # copy a file from the packages file payload to the set up scripts folder
    shutil.copy(
        f"{Path(__file__).parent.parent.absolute()}/files/preprocess.py",
        settings.PREPROCESSING_FILENAME.resolve(),
    )


def create_custom_plot_style_template() -> None:
    """Create Matplotlib custom plot style file template."""
    template_name: str = 'style_template.mplstyle'
    template_path: Path = Path(f"hifis_surveyval/files/{template_name}")
    custom_plot_styles_path: Path = Path('custom_plot_styles')
    target_path: Path = custom_plot_styles_path / Path(template_name)

    if not os.path.exists(custom_plot_styles_path.absolute()):
        os.makedirs(custom_plot_styles_path.absolute())
    if not os.path.exists(target_path.absolute()):
        shutil.copy(template_path.absolute(), target_path.absolute())
