from typing import Sequence

import matplotlib.pyplot as plt
from matplotlib import cycler, font_manager

from kilroyplot import fonts

STYLE = "seaborn"
DPI = 90
FONT_FAMILY = "Quicksand"
FONT_WEIGHT = "bold"
COLOR_SCHEME = ("#787CE0", "#E09290", "#6EE095", "#E0C863")


def add_fonts() -> None:
    for font_file in fonts.paths:
        font_manager.fontManager.addfont(font_file)


def configure(
        style: str = STYLE,
        dpi: int = DPI,
        font_family: str = FONT_FAMILY,
        font_weight: str = FONT_WEIGHT,
        color_scheme: Sequence[str] = COLOR_SCHEME
) -> None:
    plt.style.use(style)
    plt.rcParams.update(
        {
            "figure.dpi": dpi,
            "font.family": font_family,
            "font.weight": font_weight,
            "axes.labelweight": font_weight,
            "axes.titleweight": font_weight,
            "axes.prop_cycle": cycler(color=color_scheme),
            'mathtext.default': 'regular'
        }
    )


configure()
