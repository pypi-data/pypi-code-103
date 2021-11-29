import numpy as np
import inflect
from scipy.stats import iqr
from math import floor, log


class PandasTransformFuncs:
    @staticmethod
    def calc_mean(x):
        return np.mean(x)

    @staticmethod
    def calc_iqr(x):
        return iqr(x)

    @staticmethod
    def calc_median(x):
        return np.median(x)

    @staticmethod
    def calc_iqr_score(x):
        return (x-np.median(x))/iqr(x)

    @staticmethod
    def calc_row_count(x):
        return len(x)


class HumanReadableTextFormatting:
    @classmethod
    def format_col(cls, x, method):
        assert np.isfinite(
            x), f'NaN and Inf values not permitted for formatting, current value = {x}'

        if method == 'dollar':
            return f'${round(x):,}'
        if method == 'dollar-short':
            return f'${cls._longnum2string(x)}'
        if method == 'percent':
            return f'{cls._decimal2percent(x)}%'
        if method == 'inflect':
            return inflect.engine().number_to_words(x)

    @staticmethod
    def _decimal2percent(x):
        if x == 0:
            return 0

        # take absolute value of x when getting n digits
        # can't log a negative
        n_digits = np.max((np.floor(-np.log10(np.abs(x))), 0))
        m1 = 10**(2 + n_digits)
        m2 = 10**(n_digits)
        pct = round(x*m1)/m2
        if n_digits == 0:
            pct = round(pct)
        return pct

    @staticmethod
    def _longnum2string(x, min_digits=2):
        if x == 0:
            return '0'

        if x < 0:
            sign = '-'
            x = -x
        else:
            sign = ''

        units = ['', 'K', 'M', 'G', 'T', 'P']
        k = 1000.0
        magnitude = int(floor(log(x, k)))
        magnitude = np.max((magnitude, 0))

        # first get the rounded value
        value = round(x / (k**(magnitude)))
        value_len = len(str(value))

        # if length of rounded value is < min digits
        # add digits to rounded value
        if value_len < min_digits and x > k:
            value = x / (k**(magnitude))
            n_decimals = min_digits - value_len
            value = round(value*(10**n_decimals))/(10**n_decimals)

        return f'{sign}{value}{units[magnitude]}'

    @staticmethod
    def html_text_augment(x, methods):
        tags = {
            'bold': 'b',
            'italics': 'i'
        }

        for m in methods:
            x = f"<{tags[m]}>{x}</{tags[m]}>"
        return x

    @staticmethod
    def add_br_to_title(x, n_chars):

        arr = x.split()

        counter = 0
        out_str = ''
        for idx, w in enumerate(arr):
            counter += len(w)
            if counter >= n_chars and idx > 0:
                out_str += f'<br>{w}'
                counter = 0
            else:
                out_str += f' {w}'

        return out_str.strip()


def decimal_2_percent(x, n_decimals=0):
    return round(x*10**(n_decimals+2))/10**(n_decimals)


def distlr_fig_formatting(fig):

    fig_params = {
        'theme': [
            '#0071EB',
            '#001A70',
            '#838D9C',
            '#05152D'
        ],
        'fig_width': 282,
        'fig_height': 325,
        'axis_font_size': 10,
        'data_label_font_size': 12,
        'titlefont_size': 12
    }

    format_fig_layout(fig, fig_params)

    axes_updates(fig, fig_params)

    fig.for_each_trace(
        lambda trace: UpdateTraceClass(
            trace=trace, fig_params=fig_params).update_parent()
    )

    return fig


def format_fig_layout(fig, fig_params):
    n_rows = len(fig._grid_ref)

    # adjust fig height based on number of figures
    # .75 fig_height for every fig greater than 1
    fig_height = n_rows * fig_params['fig_height']
    fig_width = fig_params['fig_width']

    fig.update_layout(
        titlefont_size=12,
        width=fig_width,
        height=fig_height,
        margin=dict(l=5, r=5, t=50, b=5),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
        font_family="'Roboto' sans-serif",
        bargap=0,  # bar graph sepcific updates
        bargroupgap=0,
        hovermode=False
    )

    fig.update_annotations(
        font_size=fig_params['data_label_font_size'],
        # y=1.05, yanchor='bottom', yref='paper'
    )

    fig.update_yaxes(
        showline=True,
        showgrid=True,
        gridwidth=0,
        gridcolor='#EEF0F1',
        linewidth=1,
        linecolor='#C8CDD5',
        titlefont_size=fig_params['axis_font_size'],
        tickfont_size=fig_params['axis_font_size']
    )

    fig.update_xaxes(
        showline=True,
        linewidth=1,
        linecolor='#C8CDD5',
        titlefont_size=10,
        tickfont_size=10
    )


def axes_updates(fig, fig_params):
    # all updates involving the x and y axes, only working for
    # scatter and bar right now
    x_trace_dict = build_trace_axis_dict(fig, axis='x')
    assign_colors_from_dict(x_trace_dict, fig_params['theme'])
    update_bar_width_from_dict(x_trace_dict)

    y_trace_dict = build_trace_axis_dict(fig, axis='y')
    update_yaxis_from_dict(fig, y_trace_dict)

    y_trace_dict = build_trace_axis_dict(fig, axis='y', secondary_y=True)
    update_yaxis_from_dict(fig, y_trace_dict)


def build_trace_axis_dict(fig, axis='x', secondary_y=False):

    if axis == 'x':
        print("secondary_y only valid when axis = 'y', forcing None")
        secondary_y = None

    traces = [f for f in fig.select_traces(secondary_y=secondary_y)]
    trace_dict = {}

    anchor_axis = {'x': 'y', 'y': 'x'}[axis]
    trace_key = f'{axis}axis'
    anchor_key = f'{anchor_axis}axis'

    '''
    need to add additional condition to selector
    function treats secondary and primary y axes seperately
    there isnt a secondary_y attribute in trace, but 
    can be selected via select_traces
    essentially the function adds 1 the subplot indexing when secondary_y = True
    '''

    if secondary_y == True:
        yside = 'right'
    else:
        yside = None

    for t in traces:
        if hasattr(t, trace_key):
            trace_label = getattr(t, trace_key)
            if trace_label == None:
                trace_label = axis
            '''
            anchor used for select axes, 
            sometimes, if there is only one axis, trace label is none, but axis is still 'x' or 'y'
            the anchor for an axis is the adjecent axis
            so we need two things an anchor_key lookup
            and an index tied to the specific anchoring axis
            '''

            if trace_label == None:
                anchor = anchor_axis
            else:
                anchor = getattr(t, anchor_key)

            if trace_label in trace_dict.keys():
                trace_dict[trace_label]['trace'] += [t]
            else:
                trace_dict[trace_label] = {
                    'trace': [t],
                    'selector': {'anchor': anchor, 'side': yside}
                }

    return trace_dict


def update_yaxis_from_dict(fig, trace_dict):
    for ax, vals in trace_dict.items():
        ax_data = np.concatenate([getattr(t, 'y')
                                 for t in vals['trace'] if hasattr(t, 'y')])
        ymin, ymax, step = get_new_axis_range(ax_data)
        # exception for very small range values
        # don't update if ymin = ymax
        tick_steps = np.arange(ymin, ymax, step)
        if ymin < 0 and ymax > 0:
            # shift to include origin if negative values in range
            fig.update_yaxes(
                zeroline=True,
                zerolinewidth=1.1,
                zerolinecolor='#C8CDD5'
            )
            tick_steps = shift_steps_include_origin(tick_steps)

        # down sample last step, dont re adjust min max, just take fewer ticks
        tick_steps = downsample_steps(tick_steps)
        print('yaxis details:')
        print(ymin, ymax)
        print(tick_steps)

        fig.update_yaxes(
            selector=vals['selector'],
            tickmode='array',

            tickvals=tick_steps[1:],
            range=[ymin, ymax],
        )


def get_new_axis_range(fig_data):

    ymin = np.min(fig_data)
    ymax = np.max(fig_data)

    ymin, ymax, rng = rescale_min_max_for_data_labels(ymin, ymax)

    step = rng/4
    print('step', step)
    step = adjust_step(step)
    print('adjusted_step', step)

    # min up or max down, depending on axis range
    if ymin > 0:
        ymin = round_x_to_nearest_y(ymin, step, method='floor')

    if ymax < 0:
        ymax = round_x_to_nearest_y(ymax, step, method='ceil')

    # ymax=round_x_to_nearest_y(ymax, step, method = 'ceil')
    return ymin, ymax, step


def rescale_min_max_for_data_labels(ymin, ymax):
    rng = ymax-ymin
    print('before scaling', ymin, ymax)
    # rescale to add buffer for data labels
    if ymin == ymax:
        ymin *= .95
        ymax *= 1.05

    if ymin >= 0 and ymax > 0:
        ymax += rng * .15
    if ymin < 0 and ymax <= 0:
        ymin -= rng + .05
        ymax += rng + .1
    if ymin < 0 and ymax > 0:
        ymin -= rng * .125
        ymax += rng * .125

    rng = ymax-ymin
    print('after scaling', ymin, ymax)
    return ymin, ymax, rng


def adjust_step(step):

    modifier = 1
    return np.power(10, np.floor(np.log10(step))) * modifier


def round_x_to_nearest_y(x, y, method='ceil'):
    if method == 'ceil':
        return np.ceil(x/y)*y
    elif method == 'floor':
        return np.floor(x/y)*y


def shift_steps_include_origin(tick_steps):
    # if more ticks greater than zero, shift down
    # else shift up
    if (tick_steps > 0).sum()/len(tick_steps) >= 0.5:
        shift = tick_steps[tick_steps > 0].min()
    else:
        shift = tick_steps[tick_steps < 0].max()

    tick_steps -= shift
    return tick_steps


def downsample_steps(tick_steps, max_ticks=6):
    n_ticks = len(tick_steps)
    if n_ticks > max_ticks:
        sample_factor = int(np.ceil(n_ticks / max_ticks))
        tick_steps = np.array([tick_steps[idx]
                               for idx in range(0, n_ticks, sample_factor)])
    return tick_steps


def assign_colors_from_dict(trace_dict, theme):
    n_colors = len(theme)
    for key, vals in trace_dict.items():
        traces = vals['trace']

        if len(traces) == 1:
            trace = traces[0]
            if trace.type == 'bar':
                color = [theme[idx % n_colors]
                         for idx, c in enumerate(trace.x)]
                trace.update({'marker_color': color})
            elif trace.type == 'scatter':
                # give maker and line different colors when only one trace
                # marker darker than line, just personal choice
                trace.update({
                    'marker_color': theme[1],
                    'line_color': theme[0]
                })

        else:
            for idx, trace in enumerate(traces):
                color = theme[idx % n_colors]
                if trace.type == 'bar':
                    trace.update({'marker_color': color})
                elif trace.type == 'scatter':
                    trace.update({
                        'marker_color': color,
                        'line_color': color
                    })


def update_bar_width_from_dict(trace_dict):
    '''
    With bargap=0 and bargroupgap=0 (set in fig formatting)
    You want the width parameter to range somewhere between 0 and 1
    Ploty splits the x axis into equal sections according to the 
    number of distinct x values. 
    When width = 1, each bar occupies the full space of it's respective section
    With grouped bar, 1/(n_bars per group) is the maximum width without overlapping
    Currently setting the max width to 0.75, so there's a bit of spacing between sections
    Then divide by number of traces to account for possible grouping
    '''
    base_width = 0.3

    for key, vals in trace_dict.items():
        traces = [trace for trace in vals['trace'] if trace.type == 'bar']
        for trace in traces:
            # do in loop, otherwise possible divid by zero error
            bar_width = np.min((base_width, 1/len(traces)))
            trace.update({'width': bar_width})


def cap_ymax(ymax, tick_steps, ydata):
    if tick_steps[-1] > np.max(ydata):
        ymax = tick_steps[-1]

    return ymax


#not used
def update_plot_grid(fig):
    for idx in range(len(fig.data)):
        if fig.data[idx].type == 'bar':
            fig = add_grid_update_yaxis(fig, idx)
    return fig

# not used, grid is too messy, with all possible combinations
# of primary and secondary axes and subplot positions etc. maybe revisit


def add_grid_update_yaxis(fig, idx):
    fig_data = fig.data[idx]
    n_bars = len(fig_data.x)
    ymin, ymax, step = get_new_axis_range(fig_data.y)
    # exception for very small range values
    if step > 0:
        print('doing something')
        tick_steps = np.arange(ymin, ymax, step)
        tick_steps = downsample_steps(tick_steps, ymax)

        # if range is negative, shift to include zero as step
        print(ymin)
        print(ymin < 0)
        if ymin < 0:
            tick_steps = shift_steps_include_origin(tick_steps)
            #ymin = tick_steps.min()
            #ymax = tick_steps.max()

        # probably no need to cap ymax, just keep it at original calculated ymax
        # ymax=cap_ymax(ymax, tick_steps, fig_data.y)
        print('yaxis details:')
        print(ymin, ymax)
        print(tick_steps)

        fig.update_yaxes(
            tickmode='array',
            tickvals=tick_steps,
            range=[ymin, ymax],
            row=idx+1, col=1
        )

        # dont draw line for first tick
        for y in tick_steps[1:]:
            fig.add_shape(type="line",
                          xref='paper', x0=-0.5, y0=y, x1=n_bars-0.5, y1=y,
                          line=dict(
                              color="#C8CDD5",
                              width=1.5,
                              dash="dot",

                          ),
                          layer='below',
                          row=idx+1, col=1
                          )
    return fig
# cap the max value if the maximum tick value is already
# larger than the max y value


class UpdateTraceClass():
    def __init__(self, trace, fig_params):
        self.trace = trace
        self.theme = fig_params['theme']

        self.trace_width = fig_params['fig_width']
        self.axis_font_size = fig_params['axis_font_size']
        self.data_label_font_size = fig_params['data_label_font_size']

    def update_parent(self):
        if self.trace.type == 'bar':
            self.update_bar()

        if self.trace.type == 'table':
            self.update_table()

        # if self.trace.type == 'scatter':
        #   self.update_scatter()

    def update_scatter(self):
        # self._update_bar_xlabels()

        update_dict = {
            'mode': 'lines+markers',
            'line': dict(color=self._get_bar_colors)
        }
        self.trace.update(update_dict)

    def update_bar(self):
        self._update_bar_xlabels()

        update_dict = {
            'textposition': 'outside',
            'outsidetextfont': {'size': self.axis_font_size},
        }
        self.trace.update(update_dict)

    def _update_bar_xlabels(self):
        n_labels = len(self.trace.x)
        n_chars = self.trace_width/(n_labels+2)/self.axis_font_size

        self.trace.x = [HumanReadableTextFormatting.add_br_to_title(
            label, n_chars) for label in self.trace.x]

    def update_table(self):
        self.trace.update({
            'cells': {
                'fill_color': '#FFFFFF',
                'line_color': '#C8CDD5',
                'line_width': 1,
                'font': {'size': self.data_label_font_size}
            },
            'header': {
                'fill_color':  '#001A70',
                'line_color': '#C8CDD5',
                'line_width': 1,
                'font': {'size': self.axis_font_size, 'color': 'white'}
            }
        })
