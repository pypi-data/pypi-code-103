import pandas as pd
import matplotlib.pyplot as plt
import pandas.core.series

from . import xsettings


def match_key_value(values, hard_coded=None):
    hard_coded = hard_coded or dict()
    seen = dict()

    def get_value(key):
        key = str(key)

        if key in hard_coded:
            return hard_coded[key]

        if key in seen:
            return seen[key]

        seen[key] = values[len(seen) % len(values)]
        return seen[key]

    get_value.seen = seen
    get_value.values = values
    get_value.hard_coded = hard_coded

    return get_value


def match_colors(default_colors=None, hard_coded_colors=None):
    default_colors = xsettings.get_default(xsettings.DEFAULT_COLORS, default_colors)
    hard_coded_colors = xsettings.get_default(xsettings.HARD_CODED_COLORS, hard_coded_colors)

    return match_key_value(default_colors, hard_coded=hard_coded_colors)


def match_markers(default_markers=None, hard_coded_markers=None):
    default_markers = xsettings.get_default(xsettings.DEFAULT_MARKERS, default_markers)
    hard_coded_markers = xsettings.get_default(xsettings.HARD_CODED_MARKERS, hard_coded_markers)

    return match_key_value(default_markers, hard_coded=hard_coded_markers)


def update_axes(x=None, y=None):
    if isinstance(x, pd.Series):
        x = x.name

    if isinstance(y, pd.Series):
        y = y.name

    try:
        x = xsettings.COL_DESC.get(x, x)
        y = xsettings.COL_DESC.get(y, y)
    except TypeError:
        return

    if x:
        plt.xlabel(x)

    if y:
        plt.ylabel(y)


def decorate(x=None, y=None, xlim=None, ylim=None, title=None, show=False):
    update_axes(x=x, y=y)

    if xlim:
        plt.xlim(xlim)

    if ylim:
        plt.ylim(ylim)

    if title:
        plt.title(title)

    # plt.legend()
    plt.tight_layout()

    if show:
        plt.show()


def monkey_patch_x_y(package, fname):
    f = getattr(package, fname)

    def f_new(x, y, *args, **kwargs):
        ret = f(x, y, *args, **kwargs)
        update_axes(x, y)
        return ret

    setattr(package, f"_{fname}_orig", f)
    setattr(package, fname, f_new)


def monkey_patch_x(package, fname):
    f = getattr(package, fname)

    def f_new(x, *args, **kwargs):
        ret = f(x, *args, **kwargs)
        update_axes(x)
        return ret

    setattr(package, f"_{fname}_orig", f)
    setattr(package, fname, f_new)


def monkey_patch():
    for fname in ['scatter', 'plot']:
        monkey_patch_x_y(plt, fname)

    for fname in ['hist']:
        monkey_patch_x(plt, fname)
