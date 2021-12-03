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

"""Module offers functionality to create color maps and fill pattern maps."""
from enum import Enum
from typing import Dict, List

from matplotlib import colors, pyplot


class FillPattern(Enum):
    """Represents different fill patterns in Matplotlib plots."""

    PATTERN_01 = 1
    PATTERN_02 = 2
    PATTERN_03 = 3
    PATTERN_04 = 4
    PATTERN_05 = 5
    PATTERN_06 = 6
    PATTERN_07 = 7
    PATTERN_08 = 8
    PATTERN_09 = 9
    PATTERN_10 = 10


class DefaultFillPattern:
    """Defines a default fill pattern map to be used in plots."""

    # Define mapping from enum FillPattern to string representation of fill
    # pattern.
    SLASH_FILL_PATTERN: Dict[FillPattern, str] = {
        FillPattern.PATTERN_01: '#FFFFFF',
        FillPattern.PATTERN_02: '/',
        FillPattern.PATTERN_03: '//',
        FillPattern.PATTERN_04: '///',
        FillPattern.PATTERN_05: '////',
        FillPattern.PATTERN_06: '#000000',
    }


class CustomColors(Enum):
    """Represents different colors in Matplotlib plots."""

    CUSTOM_01 = 1
    CUSTOM_02 = 2
    CUSTOM_03 = 3
    CUSTOM_04 = 4
    CUSTOM_05 = 5
    CUSTOM_06 = 6


class DefaultColors:
    """Defines default colors to be used in plots."""

    # Define mapping from enum Colors to hex representation of colors.
    HELMHOLTZ_BLUE: Dict[CustomColors, str] = {
        CustomColors.CUSTOM_01: "#99BDD9",
        CustomColors.CUSTOM_02: "#669CC6",
        CustomColors.CUSTOM_03: "#337BB3",
        CustomColors.CUSTOM_04: "#005AA0",
        CustomColors.CUSTOM_05: "#004880",
        CustomColors.CUSTOM_06: "#002D50",
    }


class ColorMapParameters:
    """Creates a color map and a fill pattern map from parameters."""

    def __init__(
        self,
        number_colors_required: int = None,
        use_color: bool = True,
        use_pattern: bool = False,
        color_map_name: str = None,
        use_inverted_color_map: bool = False,
        brightness_factor: float = 1.0,
        custom_color_map: Dict[Enum, str] = DefaultColors.HELMHOLTZ_BLUE,
        pattern_map: Dict[Enum, str] = DefaultFillPattern.SLASH_FILL_PATTERN
    ) -> None:
        """
        Initialize parameters and creates color map and fill pattern map.

        Args:
            number_colors_required (int):
                Number to specify how many colors are needed.
            use_color (bool):
                Flag to specify whether to fill plot objects with colors.
            use_pattern (bool):
                Flag to specify whether to fill plot objects with patterns.
            color_map_name (str):
                Name of the color map to use.
            use_inverted_color_map (bool):
                Flag to specify whether color map need to be inverted.
            brightness_factor (float):
                Number to specify brightness of colors in color map.
            custom_color_map (Dict[CustomColors, str]):
                List to specify custom colors in a color map.
            pattern_map (Dict[FillPattern, str]):
                Dictionary of FillPattern to hatch pattern string mappings.
        """
        self._number_colors_required: int = number_colors_required
        self._use_color: bool = use_color
        self._use_pattern: bool = use_pattern
        self._color_map_name: str = color_map_name
        self._use_inverted_color_map: bool = use_inverted_color_map
        self._brightness_factor: float = brightness_factor
        self._custom_color_map: Dict[CustomColors, str] = custom_color_map
        self._fill_pattern_map: Dict[FillPattern, str] = pattern_map
        self._color_map: colors.Colormap = None
        self._pattern_map: List[str] = None
        self.create_color_map_and_patterns()

    @property
    def use_color(self) -> bool:
        """Access for use color flag."""
        return self._use_color

    @property
    def use_pattern(self) -> bool:
        """Access for use pattern flag."""
        return self._use_pattern

    @property
    def color_map(self) -> colors.Colormap:
        """Access color map property."""
        return self._color_map

    @property
    def pattern_map(self) -> List[str]:
        """Access fill pattern map property."""
        return self._pattern_map

    def create_color_map_and_patterns(self) -> None:
        """Create a color map and fill pattern map from parameters."""
        # Custom color map is given
        if self._color_map_name is None and self._custom_color_map is not None:
            color_count = len(self._custom_color_map)
            # Set number of colors required to number of all colors in custom
            # map if not number is given.
            if self._number_colors_required is None:
                self._number_colors_required = color_count
            # Raise exception if there are not enough colors in the
            # selected color map.<
            if self._number_colors_required > color_count:
                raise NotImplementedError(
                    f"Attempt to plot a chart "
                    f"with more then {color_count} columns."
                    f"Color palette has not enough colors for all of them."
                )
            # Reduce the colormap to have only as much colors as there
            # are columns so each columns color index matches the column
            # index.
            color_map_list = []
            for index in range(1, self._number_colors_required + 1):
                # Get color specified in custom color map at respective
                # position
                color = self._custom_color_map[CustomColors(index)]
                # Use color specified in pattern map if given
                if not self._use_color and self._use_pattern:
                    if FillPattern(index) in self._fill_pattern_map and \
                            '#' in self._fill_pattern_map[FillPattern(index)]:
                        # Use bar color specified in pattern map
                        color = self._fill_pattern_map[FillPattern(index)]
                    else:
                        # Use bar color white in case of hatch patterns given
                        color = '#FFFFFF'
                # Use a brightness factor that modifies the color in
                # all color components.
                color_modified = [component * self._brightness_factor
                                  for component in colors.to_rgb(color)]
                color_map_list.append(color_modified)
            self._color_map = colors.ListedColormap(color_map_list)
        else:
            # No custom color map given, hence use pre-defined color map
            # Use default color map if no color map name is given
            if self._color_map_name is None:
                self._color_map_name = "Pastel1"
            # Use specified color map or the inverted counterpart
            map_name = self._color_map_name \
                if not self._use_inverted_color_map \
                else self._color_map_name + "_r"
            self._color_map = pyplot.get_cmap(map_name)
            color_count = len(self._color_map.colors)
            # Raise exception if there are not enough colors in the
            # selected color map.
            if self._number_colors_required > color_count:
                raise NotImplementedError(
                    f"Attempt to plot a chart "
                    f"with more then {color_count} columns."
                    f"Color palette has not enough colors for all of them."
                )
            # Reduce the colormap to have only as much colors as there
            # are columns so each columns color index matches the column
            # index.
            color_map_list = []
            for index in range(self._number_colors_required):
                # Get color specified in color map at respective position
                color = self._color_map.colors[index]
                # Use color specified in pattern map if given
                if not self._use_color and self._use_pattern:
                    if FillPattern(index + 1) in self._fill_pattern_map and \
                            '#' in self._fill_pattern_map[
                                FillPattern(index + 1)]:
                        # Use bar color specified in pattern map
                        color = self._fill_pattern_map[FillPattern(index + 1)]
                    else:
                        # Use bar color white in case of hatch patterns given
                        color = '#FFFFFF'
                # Use a brightness factor that modifies the color in
                # all color components.
                color_modified = [component * self._brightness_factor
                                  for component in color]
                color_map_list.append(color_modified)
            self._color_map = colors.ListedColormap(color_map_list)

        # Generate pattern map
        self._pattern_map = None
        if self._fill_pattern_map is not None:
            # Raise exception if there are not enough patterns in the selected
            # pattern map.
            if self._number_colors_required > len(self._fill_pattern_map):
                raise NotImplementedError(
                    f"Attempt to plot a chart "
                    f"with more then {color_count} columns."
                    f"Color palette has not enough colors for all of them."
                )
            # Reduce the pattern  map to have only as much patterns as there
            # are columns so each columns pattern index matches the column
            # index.
            self._pattern_map = [
                self._fill_pattern_map[key]
                for key in self._fill_pattern_map.keys()
            ]
