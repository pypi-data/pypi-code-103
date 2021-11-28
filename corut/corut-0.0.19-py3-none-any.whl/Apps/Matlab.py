#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Some facilitating functions for matlab
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

from matplotlib import pyplot
from matplotlib.dates import DateFormatter, HourLocator
from ..Shell import print_error


def create_chart_pie(data, out_file=None, *args, **kwargs):
    """
    create_chart_pie(
        data={
            '1': {
                'values': [3628, 2143, 23],
                'labels': ['Pass', 'Fail  ', 'Error'],
                'colors': ['green', 'red', 'yellow'],
                'loc': 'lower center',
                'set_title': 'Test Result',
                'label_title': 'Total: 5794'
            },
            '2': {
                'values': [0, 120, 2, 5671],
                'labels': ['Audio', 'Photo', 'Video', 'String'],
                'colors': ['orange', 'black', 'blue', 'grey'],
                'loc': 'lower center',
                'set_title': 'Comparison Operations',
                'label_title': 'Total: 5881'
            }
        }
    )
    :param data: List of values to be displayed on the chart.
    :param out_file: Image path information to be saved.
    """
    try:
        assert (isinstance(data, dict)), "All values must be entered as dictionary."
        ax = {}
        fig = pyplot.figure()
        for index, pie in enumerate(data):
            data_swap = {
                'values': None, 'labels': None, 'colors': None,
                'loc': None, 'set_title': None, 'label_title': None
            }
            data_swap.update(data.get(pie))
            values, labels, colors, loc, set_title, label_title = data_swap.values()
            ax[str(index)] = fig.add_subplot(121+index)
            ax[str(index)].pie(
                values,
                colors=colors,
                labels=[
                    j if j != '0.0%' else '' for j in
                    [f'{100*i/sum(values):.1f}%' for i in values]
                ],
                shadow=True,
                startangle=divmod(33*index, 360)[1], *args, **kwargs
            )
            ax[str(index)].legend(
                labels=[f'{j}:{i}' for i, j in zip(values, labels)],
                loc=loc,
                title=label_title,
                fontsize=7
            )
            ax[str(index)].set_title(set_title)
            ax[str(index)].axis('equal')
        pyplot.axis('equal')
        pyplot.tight_layout()
        # pyplot.show()
        if out_file:
            pyplot.savefig(out_file)
        pyplot.close()
        print(f'Matlab image created successfully...:{out_file}')
    except Exception as error:
        print_error(error, locals())


def create_chart_bar(
        x_data, y_data, bar_label, bar_color, bar_value_color, x_label, y_label, title,
        y_line_value, y_line_color, out_file
):
    """
    create_chart_bar(
        x_data=[
            '06/07/2020', '07/07/2020', '08/07/2020', '09/07/2020', '10/07/2020',
            '11/07/2020', '12/07/2020'
        ],
        y_data=[06.62, 07.51, 08.69, 08.63, 08.32, 08.35, 08.58],
        bar_label='Average',
        bar_color='blue',
        bar_value_color='red',
        x_label='Days',
        y_label='Seconds',
        y_line_value=15.0,
        y_line_color='red',
        title='Create Chart Bar',
        out_file=r'create_chart_bar.png'
    )
    :param x_data: List of names for each bar.
    :param y_data: List of values to be displayed on the bar.
    :param bar_label: Label for bar.
    :param bar_color: Color information of the bars.
    :param bar_value_color: String color of values written on the bar.
    :param x_label: Label at the bottom of the chart.
    :param y_label: Label to the left of the chart.
    :param title: Name information to be given to the chart.
    :param y_line_value: Creates a line to specify any interval between x values.
    :param y_line_color: Makes a color cast for y_line_value
    :param out_file: Image path information to be saved.
    """
    try:
        assert (isinstance(y_data, list)), "Must be [1, 2, 3, 4, ...]"
        assert (
                isinstance(bar_label, str) and
                isinstance(bar_color, str) and
                isinstance(bar_value_color, str)
        ), "All values must be entered as strings."
        fig, ax = pyplot.subplots()
        b = pyplot.bar(x_data, y_data, label=bar_label, color=bar_color)
        pyplot.legend()
        pyplot.gcf().autofmt_xdate()
        for value in b:
            pyplot.text(
                value.get_x() + value.get_width() / 2., value.get_height(), value.get_height(),
                ha='center', va='bottom', color=bar_value_color
            )
        ax.set(xlabel=x_label, ylabel=y_label, title=title)
        y_data_max_value = max(y_data)
        if y_data_max_value < y_line_value:
            y_data_max_value += y_line_value
        else:
            y_data_max_value = max(y_data) + (max(y_data) / 100 * 33)
        pyplot.ylim(0, y_data_max_value)
        pyplot.axhline(y=y_line_value, linewidth=1, color=y_line_color)
        pyplot.savefig(out_file)
        # pyplot.show()
        pyplot.close()
        print(f'Matlab image created successfully...:{out_file}')
    except Exception as error:
        print_error(error, locals())


def create_chart_line(
        data, set_plot_text, max_y, line_extra_y, label_x, label_y, title, out_file
):
    try:
        assert (isinstance(data, list)), "Must have list value. For example [[x, y, label], ...]"
        assert (
                isinstance(set_plot_text, list)
        ), "Must have list value. For example [[x, y, value], ...]"
        assert (isinstance(max_y, float)), "Must have float value"
        assert (
                isinstance(line_extra_y, list)
        ), "Must have list value. For example [[15, 'green'], [30, 'orange']]"
        assert (
                isinstance(label_x, str) and isinstance(label_y, str) and isinstance(title, str)
        ), "Must have string value"
        fig, ax = pyplot.subplots(figsize=(17, 9))
        for (x, y, label) in data:
            ax.plot(x, y, label=label, linewidth=1.5)
        # for (x, y, value) in set_plot_text:
        #     new_color = 'black'
        #     for (line, color) in line_extra_y:
        #         if value >= line:
        #             new_color = color
        #             break
        #     ax.text(x, y, value, color=new_color, rotation=45)
        ax.set(xlabel=label_x, ylabel=label_y, title=title)
        pyplot.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))
        pyplot.gca().xaxis.set_major_locator(HourLocator())
        for (line, color) in line_extra_y:
            pyplot.axhline(y=line, linewidth=2, color=color)
        # pyplot.ylim(0, int(float(max_y + (max_y / 100 * 100))))
        pyplot.yticks([i for i in range(0, round(int(max_y) + 9, -1) + 1, 2)])
        pyplot.xticks(set_plot_text[0], set_plot_text[1])
        pyplot.legend()
        # pyplot.gcf().autofmt_xdate()
        pyplot.gcf()
        pyplot.gca()
        pyplot.savefig(out_file)
        # pyplot.show()
        pyplot.close()
        print(f'Matlab image created successfully...:{out_file}')
    except Exception as error:
        print_error(error, locals())


class Matlab:
    create_chart_pie = staticmethod(create_chart_pie)
    create_chart_bar = staticmethod(create_chart_bar)
    create_chart_line = staticmethod(create_chart_line)
