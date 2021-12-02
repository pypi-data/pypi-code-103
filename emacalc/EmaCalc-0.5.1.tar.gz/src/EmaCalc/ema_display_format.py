"""This module includes functions to format output displays of
EmaModel results,
in graphic and textual form.

Some formatting details are defined by module global variables,
which can be modified by user.

*** Version History:

2021-11-07, copied and modified PairedCompCalc -> EmaCalc
"""
# *** NEED format switches for all special chars differing between latex and tab variants

import numpy as np
from itertools import cycle, product
import matplotlib.pyplot as plt
import logging

plt.rcParams.update({'figure.max_open_warning': 0})
# suppress warning for many open figures

logger = logging.getLogger(__name__)


# --------------------------- Default format parameters:
FMT = {'colors': 'rbgk',    # to separate results in plots, cyclic
       'markers': 'oxs*_',  # corresponding markers, cyclic use
       'table_format': 'latex',  # or 'tab' for tab-delimited tables
       'figure_format': 'pdf',   # or 'jpg', 'eps', or 'png', for saved plots
       'show_intervals': True,  # include median response thresholds in plots
       'attribute': 'Attribute',  # heading in tables
       'group': 'Group',  # heading in tables
       'credibility': 'Credibility',  # heading in tables
       # 'scale_unit': '',  # scale unit for attribute plot axis
       }
# = module-global dict with default settings for display details
# that may be changed by user

TABLE_FILE_SUFFIX = {'latex': '.tex', 'tab': '.txt'}
# = mapping table_format -> file suffix


def set_format_param(**kwargs):
    """Set / modify module-global format parameters
    :param kwargs: dict with format variables
        to replace the default values in FMT
    :return: None
    """
    for (k, v) in kwargs.items():
        k = k.lower()
        if k not in FMT:
            logger.warning(f'Format setting {k}={repr(v)} is not known, not used')
        FMT[k] = v


def _percent():
    """Percent sign for tables
    :return: str
    """
    return '\\%' if FMT['table_format'] == 'latex' else '%'


def _gt():
    """> sign for tables
    :return: str
    """
    return '$>$' if FMT['table_format'] == 'latex' else '>'


# ---------------------------- Main Result Classes
class FigureRef:
    """Reference to a single graph instance
    """
    def __init__(self, ax, path=None, name=None):
        """
        :param ax: Axes instance containing the graph
        :param path: Path to directory where figure has been saved
        :param name: (optional) updated name of figure file
        """
        self.ax = ax
        self.path = path
        self.name = name

    def __repr__(self):
        return (f'FigureRef(ax= {repr(self.ax)}, ' +
                f'path= {repr(self.path)}, name= {repr(self.name)})')

    @property
    def fig(self):
        return self.ax.figure

    def save(self, path, name=None):
        """Save figure to given path
        :param path: Path to directory where figure has been saved
        :param name: (optional) updated name of figure file  **** never used ? ****
        :return: None
        Result: updated properties path, name
        """
        if name is None:
            name = self.name
        path.mkdir(parents=True, exist_ok=True)
        f = (path / name).with_suffix('.' + FMT['figure_format'])
        self.fig.savefig(str(f))
        self.path = path
        self.name = f.name


class TableRef:
    """Reference to a single table instance,
    formatted in LaTeX OR plain tabulated txt versions
    """
    def __init__(self, text=None, path=None, name=None):
        """
        :param text: single string with all table text
        :param path: (optional) Path to directory where tables are saved
        :param name: (optional) updated file name, with or without suffix
            suffix is determined by FMT['table_format'] anyway
        """
        # store table parts instead *****???
        self.text = text
        self.path = path
        self.name = name

    def __repr__(self):
        return (f'TableRef(text= text, ' +    # fmt= {repr(self.fmt)}, ' +
                f'path= {repr(self.path)}, name= {repr(self.name)})')

    def save(self, path, name=None):
        """Save table to file.
        :param path: Path to directory where tables are saved
        :param name: (optional) updated file name, with or without suffix
            suffix is determined by FMT['table_format'] anyway
        :return: None
        Result: updated properties path, name
        """
        if name is None:
            name = self.name
        path.mkdir(parents=True, exist_ok=True)   # just in case
        f = (path / name).with_suffix(TABLE_FILE_SUFFIX[FMT['table_format']])
        if self.text is not None and len(self.text) > 0:
            f.write_text(self.text, encoding='utf-8')
        self.path = path
        self.name = f.name


# ---------------------------------------- Formatting functions:

def fig_percentiles(q_perc,
                    case_labels,  # same input as tab_percentiles
                    # case_order=None,
                    y_label='',
                    file_label='',
                    cat_limits=None,
                    x_offset=0.1,
                    x_space=0.5, **kwargs):
    """create a figure with quality percentile results
    :param q_perc: primary percentile data,
        2D or 3D array with quality percentiles, arranged as
        q_perc[p, c0, c1] = p-th percentile for (case_key_i, category_ci), i= 0, 1,
        OR
        q_perc[p, c0] if only one case dimension is included
    :param y_label: (optional) string for y-axis label
    :param cat_limits: 1D array with response-interval limits (medians)
    :param case_labels: sequence with i-th element = (case_key_i, case_labels_i), where
        case_key_i is key string for i-th case dimension,
        case_labels_i is list of string labels for i-th case dimension
        in the same order as the index order of q_perc, i.e.,
        q_perc[p].size == prod_i len(case_labels_i)
        Thus, q[p, ...,c_i,...] = percentiles for case_labels_i[c_i], i = 0,...,
        **** NOTE: currently only ONE or TWO case dimensions are allowed ***
        Plot will display case_labels_0 along x axis, and case_labels[1:] as sub-variants  *******
    :param file_label: (optional) string as first part of file name
    :param x_offset: (optional) space between case-variants of plots for each x_tick
    :param x_space: (optional) min space outside min and max x_tick values
    :param kwargs: (optional) dict with any additional keyword arguments for plot commands.
    :return: FigureRef instance with plot axis with all results
    """
    # **** input case_labels as dict OR sequence of (key, value) pairs
    # *** generalize for several case dimensions i.e., (c_0,..,c_i,...) ?
    # *** allow user to switch main / sub- dimensions by case_order input ?
    # -------------------------------- check input formats:
    # n_perc = q_perc.shape[0]
    case_shape = tuple(len(c_list) for (c_key, c_list) in case_labels)
    assert q_perc[0].size == np.prod(case_shape, dtype=int), 'mismatching size of q_perc vs. case_list'
    assert q_perc.shape[-1] == case_shape[-1], 'mismatching shape of q_perc vs case_list[-1]'
    if q_perc.ndim == 2:
        q_perc = q_perc[np.newaxis, ...]
        (case_head, case_list) = ('', [''])
    else:
        q_perc = q_perc.transpose((2, 0, 1))
        (case_head, case_list) = case_labels[1]
    # q_perc now indexed as q_perc[case, p, object], prepared to plot one case at a time
    (x_label, x_tick_labels) = case_labels[0]
    # ------------------------------------------------------------------
    fig, ax = plt.subplots()
    x = np.arange(0., len(x_tick_labels)) - x_offset * (len(case_list) - 1) / 2
    for (y, c_label, c, m) in zip(q_perc, case_list,
                                  cycle(FMT['colors']), cycle(FMT['markers'])):
        label = case_head + '=' + c_label
        if y.shape[0] == 1:
            ax.plot(x, y[0, :],  # marker at single point percentile,
                    linestyle='',
                    marker=m, markeredgecolor=c, markerfacecolor='w',
                    label=label,
                    **kwargs)
        elif y.shape[0] == 2:  # plot min,max line, with marker at ends
            line = ax.plot(np.tile(x, (2, 1)),
                           y,
                           linestyle='solid', color=c,
                           marker=m, markeredgecolor=c, markerfacecolor='w',
                           **kwargs)
            line[0].set_label(label)
        else:
            ax.plot(np.tile(x, (2, 1)),
                    y[[0, -1], :],  # plot min, max line, no markers
                    linestyle='solid', color=c,
                    **kwargs)
            line = ax.plot(np.tile(x, (y.shape[0] - 2, 1)),
                           y[1:-1, :],
                           linestyle='solid', color=c,  # markers only at inner percentiles
                           marker=m, markeredgecolor=c, markerfacecolor='w',
                           **kwargs)
            line[0].set_label(label)
            # set only ONE label, even if several points
        x += x_offset
    (x_min, x_max) = ax.get_xlim()
    x_min = min(x_min, -x_space)
    x_max = max(x_max, len(x_tick_labels) - 1 + x_space)
    ax.set_xlim(x_min, x_max)
    if cat_limits is not None and FMT['show_intervals']:
        _plot_response_intervals(ax, cat_limits)
    ax.set_xticks(np.arange(len(x_tick_labels)))
    ax.set_xticklabels(x_tick_labels)
    # y_unit = FMT['scale_unit']
    # if len(y_unit) > 0:
    #     ax.set_ylabel(y_label + ' (' + y_unit + ')')
    # else:
    ax.set_ylabel(y_label)  # plain without unit
    ax.set_xlabel(x_label)
    if np.any([len(cl) > 0 for cl in case_list]):
        ax.legend(loc='best')
    if len(file_label) > 0:
        file_label += '_'
    f_name = file_label + '*'.join(c_key for (c_key, c_val) in case_labels)
    return FigureRef(ax, name=f_name)


def _plot_response_intervals(ax, c_lim):
    """plot horizontal lines to indicate response-category intervals
    :param ax: axis object
    :param c_lim: 1D array with scalar interval limits
    :return: None
    """
    (x_min, x_max) = ax.get_xlim()
    return ax.hlines(c_lim, x_min, x_max,
                     linestyle='solid',
                     colors='k',
                     linewidth=0.2)


# ----------------------------------------- table displays:

def tab_percentiles(q_perc,
                    perc,
                    case_labels,
                    case_order=None,
                    cdf=None,
                    y_label='',
                    file_label=''):
    """Create table with quality percentile results.
    This function is general and can handle any dimensionality of the data.
    :param q_perc: min 2D array with quality percentiles, stored as
        q_perc[p, c0,...,ci,...] = p-th percentile in (c0,...,ci,...)-th case condition
        OR any other array indexing with same size and same element order
        q_perc.shape[0] == len(perc)
        q_perc.size == len(perc) * n_rows; with n_rows as defined by case_list
    :param perc: list of percentage values in range 0-100
        len(perc) == q_perc.shape[0]
    :param y_label: string with label of tabulated percentiles, NOT USED
    :param case_labels: sequence OR dict with elements (case_factor_i, case_labels_i), where
        case_factor_i is key string for i-th case dimension,
        case_labels_i is list of string labels for i-th case dimension
        in the same order as the index order of q and cdf, i.e.,
        len(case_labels_i) == q.shape[i+1] == cdf.shape[i], if full multi-dim index is used
        Thus, q[p, ...,c_i,...] = percentiles for case_labels_i[c_i], i = 0,...,
    :param case_order: (optional) sequence of case_label keys, one for each case column
        len(case_order) == len(case_labels)
        Table columns are ordered as defined by case_order, if specified,
        otherwise columns are ordered as case_labels.keys()
    :param cdf: (optional) min 1D array with cumulative distribution values at zero,
        cdf[c0,...,ci,...] = probability that y-variable <= 0 in (c0,...,ci,...)-th case
        OR any other array indexing with same size and same element order
        cdf.size == number of rows as defined by case_list
    :param file_label: (optional) string as first part of file name
    :return: TableRef object, with header + one line for each combination of case labels.
        Number of table rows == prod q.shape[:-1] == prod_i len(case_labels_i)
    """
    def make_row(c, q, p_0):
        """make cells for one table row
        :param c: case tuple
        :param q: percentile quality values
        :param p_0: scalar probability q <= 0
        :return: row = list with cells
            len(row) == 1 + len(c) + len(q) + 2
        """
        c_dict = dict(c)
        # already in right order, need only c.values() ******
        return ([c_dict[c_head] for c_head in case_order]
                + [f'{p:.2f}' for p in q]
                + [f'{p_0*100:.0f}' + _percent(),
                   f'{(1.-p_0)*100:.0f}' + _percent()])

    # --------------------------------------------------------------------
    case_labels = dict(case_labels)  # just in case it was a list
    if case_order is None:
        case_order = [*case_labels.keys()]
    assert len(case_order) == len(case_labels), 'Incompatible len(case_order) != len(case_list)'
    assert all(c in case_labels for c in case_order), 'Some case_order not in case_list'
    case_shape = tuple(len(c_labels) for c_labels in case_labels.values())
    n_rows = np.prod(case_shape, dtype=int)
    # = number of table rows as defined by case_list
    assert len(perc) == q_perc.shape[0], 'Incompatible q_perc.shape[0] != n of percentiles'
    assert n_rows == np.prod(q_perc.shape[1:], dtype=int), 'Incompatible size of case_list and q_perc'
    if cdf is not None:
        assert n_rows == cdf.size, 'Incompatible size of case_list and cdf'
    # -------------------------------------------------------------------
    # transpose q_perc, cdf to case_order index order:
    q_perc = np.moveaxis(q_perc, 0, -1)
    q_perc = q_perc.reshape((*case_shape, len(perc)))
    # q_perc[c_0, ..., c_i, ..., p] = p-th percentile in (c0,...,ci,...)-th case
    case_keys = [*case_labels.keys()]
    case_axes = tuple(case_keys.index(c) for c in case_order)
    q_perc = q_perc.transpose((*case_axes, -1))
    q_perc = q_perc.reshape((n_rows, len(perc)))
    if cdf is not None:
        cdf = cdf.reshape(case_shape)
        # cdf[c_0, ..., c_i, ...] = prob(y-variable <=0) in (c0,...,ci,...)-th case
        cdf = cdf.transpose(case_axes)
        cdf = cdf.reshape((-1,))
    # --------------------------------------------------------------------
    align = [len(case_order) * 'l', len(perc) * 'r', 2 * 'r']
    h = [*case_order] + [f'{p:.0f}' + _percent() for p in perc] + ['<= 0', '> 0']
    case_rows = product(*(product([c_i], case_labels[c_i])
                          for c_i in case_order))
    rows = [make_row(c, p, cdf_0)
            for (c, p, cdf_0) in zip(case_rows,
                                     q_perc,
                                     cdf)
            ]
    if len(file_label) > 0:
        file_label += '_'
    f_name = file_label + '*'.join(case_order)
    return TableRef(_make_table(h, rows, align), name=f_name)


# def tab_credible_diff_old(diff,
#                           diff_head,
#                           diff_labels,
#                           case_head=tuple(),
#                           case_labels=tuple(),
#                           y_label=''):
#     """Create table with credible differences among results
#     :param diff: list of tuples ((i,j), p) OR ((i,j,c), p),
#         defining jointly credible differences, indicating that
#         prob{ quality of diff_labels[i] > quality of diff_labels[j]}, OR
#         prob{ quality of diff_labels[i] > quality of diff_labels[j] | case_labels[c] }
#         AND all previous pairs } == p
#     :param diff_head: sequence with one or more key(s) to be heading column(s) with diff pairs
#     :param diff_labels: list of strings with labels of compared random-vector elements,
#         len(diff_labels) == max possible diff category index (i, j)
#     :param case_head: (optional) sequence of case factors, one for each case-dimension table column
#         len(case_heads) == len(c) for each c in case_labels
#     :param case_labels: (optional) iterator of tuples, yielding
#         case_labels[c] == (case_label1, case_label2, ...), such that
#         diff[...] == ((i,j, c), p) <=> diff[...] is valid given case_labels[c]
#         len(case_labels) == max possible case index c in diff
#         len(case_list[j]) == len(case_head), for all j
#     :param y_label: (optional) string with label of tabulated attribute
#     :return: TableRef object with header lines + one line for each credible difference,
#     """
#     # *** input diff_labels as sequence of dicts, OR sequence of tuples of (key, value) pairs
#     # *** input case_labels as sequence of dicts, OR sequence of tuples of (key, value) pairs
#     if len(diff) == 0:
#         return None
#     if type(diff_head) is not tuple:  # just in case
#         diff_head = (diff_head,)
#     diff_labels = [*diff_labels]
#     case_labels = [*case_labels]
#     align = ['l', len(diff_head) * 'l', 'c', len(diff_head) * 'l', len(case_head) * 'l', 'r']
#     y = ''
#     if len(y_label) > 0:
#         y = y_label + ':'
#     h = [y, *diff_head,
#          _gt(), *diff_head,
#          *case_head,
#          FMT['credibility'] + ' (' + _percent() + ')']
#     rows = []
#     for (d, p) in diff:
#         if len(d) == 2:
#             c_tuple = ()
#         else:
#             c_tuple = case_labels[d[2]]
#         rows.append(['AND', *diff_labels[d[0]],
#                      _gt(), *diff_labels[d[1]],
#                      *c_tuple, f'{100*p:.1f}'])
#     rows[0][0] = ''  # No AND on first row
#     # if len(y_label) > 0:  # **********************************
#     f_name = y_label + '-diff_vs_' + '*'.join(diff_head)
#     return TableRef(_make_table(h, rows, align), name=f_name)


def tab_credible_diff(diff,
                      diff_labels,
                      diff_head=tuple(),  # *** not used OR define diff_column order *****
                      case_labels=tuple(),
                      case_head=tuple(),   # *** not used OR define diff_column order *****
                      y_label='',
                      file_label=''):
    """Create table with credible differences among results
    :param diff: list of tuples ((i,j), p) OR ((i,j,c), p),
        defining jointly credible differences, indicating that
        prob{ quality of diff_labels[i] > quality of diff_labels[j]}, OR
        prob{ quality of diff_labels[i] > quality of diff_labels[j] | case_labels[c] }
        AND all previous pairs } == p
    :param diff_labels: iterator or sequence of dicts or tuples of (key, value) pairs
        with labels of compared random-vector elements, yielding
        diff_labels[i] = ((key0, value0), (key1, value1),...), defining
        diff[...] == ((i,j, c), p) <=> diff_labels[i] > diff_labels[j] with prob p
        All diff_labels elements MUST have the SAME ORDER of the keys
        len(diff_labels) == max possible diff category index (i, j)
    :param case_labels: (optional) iterator or sequence of dicts or tuples of (key, value) pairs,
        yielding
        case_labels[c] == (case_label1, case_label2, ...), such that
        diff[...] == ((i,j, c), p) <=> diff[...] is valid given case_labels[c]
        len(case_labels) == max possible case index c in diff
        len(case_list[j]) == len(case_head), for all j
    :param diff_head: (optional) sequence with all diff_labels key(s) for heading column(s) with diff pairs
    :param case_head: (optional) sequence of case factors, one for each case-dimension table column
        len(case_heads) == len(c) for each c in case_labels
    :param y_label: (optional) string with label of tabulated attribute
    :param file_label: (optional) string for first part of file name
    :return: TableRef object with header lines + one line for each credible difference,
    """
    # **** use diff_head and case_head input to change column order ? **************
    if len(diff) == 0:
        return None
    diff_labels = [*(dict(diff_label_i)  # ******** or require dict input ? ***********
                     for diff_label_i in diff_labels)]
    case_labels = [*(dict(case_label_i)  # ******** or require dict input ? ***********
                     for case_label_i in case_labels)]
    if len(diff_head) == 0:
        diff_head = [*diff_labels[0].keys()]  # ****** not used
    if len(case_labels) > 0 and len(case_head) == 0:
        case_head = [*case_labels[0].keys()]  # ****** not needed ?
    align = ['l', len(diff_head) * 'l', 'c', len(diff_head) * 'l', len(case_head) * 'l', 'r']
    y = ''
    if len(y_label) > 0:
        y = y_label + ':'
    head = [y, *diff_head,
            _gt(), *diff_head,
            *case_head,
            FMT['credibility'] + ' (' + _percent() + ')']
    rows = []
    for (d, p) in diff:
        if len(d) == 2:
            c_dict = dict()
        else:
            c_dict = case_labels[d[2]]
        rows.append(['AND', *diff_labels[d[0]].values(),
                     _gt(), *diff_labels[d[1]].values(),
                     *c_dict.values(),
                     f'{100*p:.1f}'])
    rows[0][0] = ''  # No AND on first row
    if len(file_label) > 0:
        file_label += '_'
    f_name = file_label + '*'.join(diff_head) + '-diff'
    if len(case_head) > 0:
        f_name += '_' + '*'.join(case_head)
    return TableRef(_make_table(head, rows, align), name=f_name)


# ------------------------------------------ internal help functions:
# more variants may be added for other table formats

table_begin = {'latex': lambda align: '\\begin{tabular}{' + ' '.join(c for c in align) + '}\n',
               'tab': lambda align: ''}
table_head_sep = {'latex': '\\hline\n',
                  'tab': ''}
table_cell_sep = {'latex': ' & ',
                  'tab': ' \t '}
table_row_sep = {'latex': '\\\\ \n',
                 'tab': '\n'}
table_end = {'latex': '\\hline\n\\end{tabular}',
             'tab': ''}


def _make_cell(text, col_span, fmt):
    """Format multi-column table cell, usually only for header line
    :param text: cell contents
    :param col_span: number of columns to span
    :param fmt: str key for table format
    :return: string with latex or plain cell contents
    """
    if fmt == 'latex' and col_span > 1:
        return '\\multicolumn{' + f'{col_span}' + '}{c}' + '{' + text + '}'
    else:
        return text


def _make_table(header, rows, col_alignment):
    """Generate a string with table text.
    Input:
    :param header: list with one string for each table column
    :param rows: list of rows, ehere
        each row is a list of string objects for each column in this row
    :param col_alignment: list of alignment symbols, l, r, or c
        len(col_alignment) == len(header) == len(row), for every row in rows

    :return: single string with complete table
    """
    def make_row(cells, fmt):
        return table_cell_sep[fmt].join(f'{c}' for c in cells) + table_row_sep[fmt]
    # ------------------------------------------------------------------------

    fmt = FMT['table_format']  # module global constant
    t = table_begin[fmt](col_alignment)
    t += table_head_sep[fmt]
    t += make_row(header, fmt)
    t += table_head_sep[fmt]
    t += ''.join((make_row(r, fmt) for r in rows))
    t += table_end[fmt]
    return t
