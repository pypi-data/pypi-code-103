"""Utilities for matplotlib and seaborn.

`MatWrap.configure` is called upon importing this module, which enables default config.
"""

from contextlib import AbstractContextManager
from itertools import cycle, islice
from types import ModuleType
from typing import Annotated, Any, Literal, Optional

from corgy import Corgy

_WRAPPED_NAMES = ("mpl", "plt", "sns")
__all__ = ("MatWrap", "PlottingArgs", "Plot") + _WRAPPED_NAMES

mpl: ModuleType
plt: ModuleType
sns: ModuleType


def __getattr__(name):
    if name in _WRAPPED_NAMES:
        attr = getattr(MatWrap, name)
        return attr.__func__(MatWrap)
    raise AttributeError


class MatWrap:
    """Wrapper for `matplotlib`, `matplotlib.pyplot`, and `seaborn`.

    Usage::

        # Do not import `matplotlib` or `seaborn`.
        from shinyutils.matwrap import MatWrap as mw
        # Configure with `mw.configure` (refer to `configure` docs for details).
        mw.configure()

        fig = mw.plt().figure()
        ax = fig.add_subplot(111)  # `ax` can be used normally now

        # Use class properties in `MatWrap` to access `matplotlib`/`seaborn` functions.
        mw.mpl  # returns `matplotlib` module
        mw.plt  # returns `matplotlib.pyplot` module
        mw.sns  # returns `seaborn` module

        # You can also import the module names from `matwrap`
        from shinyutils.matwrap import mpl, plt, sns

        fig = plt.figure()
        ...
    """

    _rc_defaults: dict[str, Any] = {
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.grid.which": "major",
        "axes.spines.bottom": False,
        "axes.spines.left": False,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "backend": "pgf",
        "figure.constrained_layout.use": True,
        "legend.fancybox": False,
        "legend.frameon": False,
        "pgf.rcfonts": False,
        "pgf.texsystem": "lualatex",
        "savefig.format": "pdf",
        "savefig.transparent": False,
        "scatter.marker": ".",
        "text.usetex": False,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "ytick.major.size": 0,
    }

    _mpl = None
    _plt = None
    _sns = None

    _mpl_default_rc: dict[str, Any]

    @classmethod
    def configure(
        cls,
        context: Literal["paper", "poster", "notebook"] = "paper",
        style: Literal["darkgrid", "whitegrid", "dark", "white", "ticks"] = "ticks",
        font: str = "Latin Modern Roman",
        latex_pkgs: Optional[list[str]] = None,
        backend: Optional[str] = None,
        **rc_extra,
    ):
        """Configure matplotlib and seaborn.

        Args:
            context: Seaborn context ([`paper`]/`poster`/`notebook`).
            style: Seaborn style (`darkgrid`/`whitegrid`/`dark`/`white`/[`ticks`]).
            font: Font, passed directly to fontspec (default: `Latin Modern Roman`).
            latex_pkgs: List of packages to load in latex pgf preamble.
            backend: Matplotlib backend to override default (pgf).
            rc_extra: Matplotlib params (will overwrite defaults).
        """
        rc = MatWrap._rc_defaults.copy()
        rc["pgf.preamble"] = [r"\usepackage{fontspec}"]
        rc["pgf.preamble"].append(rf"\setmainfont{{{font}}}")
        rc["pgf.preamble"].append(rf"\setsansfont{{{font}}}")
        if latex_pkgs is not None:
            for pkg in reversed(latex_pkgs):
                rc["pgf.preamble"].insert(0, rf"\usepackage{{{pkg}}}")
        rc["pgf.preamble"] = "\n".join(rc["pgf.preamble"])
        if backend is not None:
            rc["backend"] = backend
        rc.update(rc_extra)

        if cls._mpl is None:
            # pylint: disable=import-outside-toplevel
            try:
                import matplotlib
            except ImportError:
                raise ImportError("shinyutils.matwrap needs `matplotlib`") from None

            cls._mpl = matplotlib
            cls._mpl_default_rc = cls._mpl.rcParams.copy()
            cls._mpl.rcParams.update(rc)

            import matplotlib.pyplot

            try:
                import seaborn
            except ImportError:
                raise ImportError("shinyutils.matwrap needs `seaborn`") from None

            cls._plt = matplotlib.pyplot
            cls._sns = seaborn
        else:
            cls._mpl.rcParams = cls._mpl_default_rc.copy()
            cls._mpl.rcParams.update(rc)

        if "font.size" in rc:
            font_scale = rc["font.size"] / cls._mpl_default_rc["font.size"]
        else:
            font_scale = 1
        cls._sns.set(context, style, cls.palette(), font_scale=font_scale, rc=rc)

    def __new__(cls):
        raise NotImplementedError(
            "`MatWrap` does not provide instances. Use the class methods."
        )

    @classmethod
    def _ensure_conf(cls):
        if cls._mpl is None:
            cls.configure()

    @classmethod
    @property
    def mpl(cls):
        """`matplotlib` module."""
        cls._ensure_conf()
        assert cls._mpl is not None
        return cls._mpl

    @classmethod
    @property
    def plt(cls):
        """`matplotlib.pyplot` module."""
        cls._ensure_conf()
        assert cls._plt is not None
        return cls._plt

    @classmethod
    @property
    def sns(cls):
        """`seaborn` module."""
        cls._ensure_conf()
        assert cls._sns is not None
        return cls._sns

    @classmethod
    def palette(cls, n=8) -> list[str]:
        """Color universal design palette."""
        _base_palette = [
            "#000000",
            "#e69f00",
            "#56b4e9",
            "#009e73",
            "#f0e442",
            "#0072b2",
            "#d55e00",
            "#cc79a7",
        ]
        if n <= len(_base_palette):
            return _base_palette[:n]

        return list(islice(cycle(_base_palette), n))


class PlottingArgs(Corgy):
    """Plotting arguments that can be added to `ArgumentParser` instances.

    Usage::

        >>> arg_parser = ArgumentParser(add_help=False, formatter_class=Corgy)
        >>> PlottingArgs.add_to_parser(arg_parser, name_prefix="plotting")
        >>> arg_parser.print_help()
        options:
            --plotting-context str
                seaborn plotting context ({'paper'/'notebook'/'talk'/'poster'}
                default: 'paper')
            --plotting-style str
                seaborn plotting style
                ({'white'/'dark'/'whitegrid'/'darkgrid'/'ticks'} default: 'ticks')
            --plotting-font str
                font for plots (default: 'Latin Modern Roman')
            --plotting-backend str
                matplotlib backend (default: 'pgf')

    The class can also be used to create an argument group inside another `Corgy`
    class::

        class A(Corgy):
            plotting: Annotated[PlottingArgs, "plotting arguments"]
    """

    context: Annotated[
        Literal["paper", "notebook", "talk", "poster"], "seaborn plotting context"
    ] = "paper"
    style: Annotated[
        Literal["white", "dark", "whitegrid", "darkgrid", "ticks"],
        "seaborn plotting style",
    ] = "ticks"
    font: Annotated[str, "font for plots"] = "Latin Modern Roman"
    backend: Annotated[str, "matplotlib backend"] = "pgf"


class Plot(AbstractContextManager):
    """Wrapper around a single matplotlib plot.

    This class is a context manager that returns a matplotlib `axis` instance when
    entering the context. The plot is closed, and optionally, saved to a file when
    exiting the context.

    Args:
        save_file: Path to save plot to. If `None` (the default), the plot is not
            saved.
        title: Optional title for plot.
        sizexy: Size tuple (width, height) in inches. If `None` (the default), the
            plot size will be determined automatically by matplotlib.
        labelxy: Tuple of labels for the x and y axes respectively. If either value is
            `None` (the default), the corresponding axis will not be labeled.
        logxy: Tuple of booleans indicating whether to use a log scale for the x and y
            axis respectively (default: `(False, False)`).

    Usage::

        with Plot() as ax:
            # Use `ax` to plot stuff.
            ...
    """

    def __init__(
        self,
        save_file: Optional[str] = None,
        title: Optional[str] = None,
        sizexy: Optional[tuple[int, int]] = None,
        labelxy: tuple[Optional[str], Optional[str]] = (None, None),
        logxy: tuple[bool, bool] = (False, False),
    ):
        self.save_file = save_file
        self.title = title
        self.sizexy = sizexy
        self.labelxy = labelxy

        self.fig = MatWrap.plt.figure()  # type: ignore
        self.ax = self.fig.add_subplot(111)

        if logxy[0] is True:
            self.ax.set_xscale("log", nonposx="clip")
        if logxy[1] is True:
            self.ax.set_yscale("log", nonposy="clip")

    def __enter__(self):
        return self.ax

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            return

        if self.title is not None:
            self.ax.set_title(self.title)

        if self.labelxy[0] is not None:
            self.ax.set_xlabel(self.labelxy[0])
        if self.labelxy[1] is not None:
            self.ax.set_ylabel(self.labelxy[1])

        if self.sizexy is not None:
            self.fig.set_size_inches(*self.sizexy)

        if self.save_file is not None:
            self.fig.savefig(self.save_file)
        MatWrap.plt.close(self.fig)


MatWrap.configure()
