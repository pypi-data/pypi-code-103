"""Real-time dispatch plotting logic.

Functions:
new_figure
plot_component_dispatch
y_axis_scaling
assign_colors
convert_to_steps
"""

import math
import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from eagers.config.plots import (
    DEFAULT_FIG_WIDTH,
    DEFAULT_FIG_HEIGHT,
    SUPTITLE_SPACE,
    cm_parula,
)
from eagers.basic.gen_limit import chp_heat


def new_figure(project_name, gen, subnet):
    n_nets = len(subnet['network_names'])
    fig = plt.figure(figsize=(DEFAULT_FIG_WIDTH, DEFAULT_FIG_HEIGHT))
    axs = []
    gs = gridspec.GridSpec(n_nets, 1)
    fig.suptitle(f"Dispatch: {project_name}", fontsize='x-large')
    for i, net in enumerate(subnet['network_names']):
        # Create new Axes object.
        new_ax = fig.add_subplot(gs[i])
        new_ax.set_title(net.title().replace('_', ' '))
        has_stor = False
        for j in range(len(gen)):
            if 'stor' in gen[j] and net in gen[j]['subnet_node']:
                has_stor = True
                break
        if has_stor:
            # Instantiate a second axes that shares the same x-axis.
            axs.append([new_ax, new_ax.twinx()])
        else:
            axs.append([new_ax])

    # Constrain layout properly.
    gs.tight_layout(fig, rect=[0, 0, 1, 1 - SUPTITLE_SPACE])
    # Remove warning about tight_layout.
    fig.set_tight_layout(False)

    plt.ion()
    plt.show()
    return fig, axs


def plot_component_dispatch(axs, history, future, gen, subnet):
    date = [j for j in history['timestamp']]
    if not future is None:
        date.extend(future['timestamp'])
    color = assign_colors(len(gen), cm_parula)
    Ymax = []
    Ymin = []
    Yticks = []
    for j, net in enumerate(subnet['network_names']):
        gen_state = {}
        stor_state = {}
        c_plot = []
        ax1 = axs[j][0]
        for i, g in enumerate(gen):
            if any(g['name'] in k for k in subnet[net]['equipment']):
                # Get history and future data
                k = g['name']
                gen_state[k] = [j for j in history['generator_state'][k]]
                if not future is None:
                    gen_state[k].extend([j for j in future['generator_state'][k]])
                if g['type'] == 'ACDCConverter':
                    if net == 'direct_current':
                        gen_state[k] = [j*abs(g['output']['e'][0][-1]) if j>0 else j for j in gen_state[k]]
                    elif net == 'electrical':
                        gen_state[k] = [-j*g['output']['dc'][0][0] if j<0 else -j for j in gen_state[k]]
                if g['type'] == 'CombinedHeatPower' and net == 'district_heat':
                    gen_state[k] = chp_heat(g,gen_state[k])
                if 'stor' in g:
                    unusable = g['stor']['size'] - g['stor']['usable_size']
                    stor_state[k] = [j + unusable for j in history['storage_state'][k]]
                    if not future is None:
                        stor_state[k].extend([j + unusable for j in future['storage_state'][k]])
                c_plot.append([j for j in color[i]])
        try:
            plt.sca(ax1)
        except ValueError:
            # Turn interactive mode off; it's no longer being used.
            plt.ioff()
        plt.cla()
        gen_state, units, yma, ymi, yti = y_axis_scaling(gen_state, net, date)
        Ymax.append(yma)
        Ymin.append(ymi)
        Yticks.append(yti)
        if yti[0] < 0:
            g_names = list(gen_state.keys())
            for k in range(len(c_plot)):
                if any(
                    [
                        sum([gen_state[g_names[f]][t] for f in range(k - 1)])
                        < 0
                        for t in range(len(date))
                    ]
                ):
                    c_plot[k].append(
                        0.5
                    )  # appending alpha to show overlaping negative values
        ax1.set_title(net.title().replace('_', ' '))
        ax1.set_ylabel(net + ' (' + units[0] + ')')
        date_step, gen_state_step = convert_to_steps(date, gen_state)
        ax1.stackplot(
            date_step,
            gen_state_step.values(),
            labels=gen_state.keys(),
            colors=c_plot,
        )
        ax1.set_xlim(date[0], date[-1])
        ax1.set_ylim(bottom=Ymin[j], top=Ymax[j])
        ax1.set_yticks(ticks=Yticks[j])
        stor_names = list(stor_state.keys())
        if len(axs[j]) > 1:
            ax2 = axs[j][1]
            try:
                plt.sca(ax2)
            except ValueError:
                # Turn interactive mode off; it's no longer being used.
                plt.ioff()
            plt.cla()
            stor_state, units2, yma, ymi, yti = y_axis_scaling(
                stor_state, net, date
            )
        # date_step,stor_state_step = convert_to_steps(date,stor_state)
        for sn in stor_names:
            ax2.set_ylabel(
                'State-of-Charge' + units2[1], color='tab:blue'
            )  # we already handled the x-label with ax1
            # ax2.plot(date_step,stor_state_step[sn],label= sn+'_SOC', color='tab:blue')
            ax2.plot(date, stor_state[sn], label=sn + '_SOC', color='tab:blue')
            ax2.tick_params(axis='y', labelcolor='tab:blue')
            ax2.set_ylim(ymi, yma)
            ax2.set_yticks(ticks=yti)
        ax1.legend(loc='upper right')
        ax1.plot(
            [history['timestamp'][-1], history['timestamp'][-1]],
            [-1e8, 1e8],
            color='tab:cyan',
        )

    plt.draw()
    plt.pause(0.001)


def y_axis_scaling(data, net, date):
    val = [
        sum(data[f][t] for f in list(data.keys()))
        for t in range(1, len(date))
    ]
    pos = max(val)
    neg = min(val)
    if pos > neg:
        oom = max(1, 0.2 + math.log10(pos - min(neg, 0)))
    else:
        oom = 1
    if oom > 6.30103:
        if net == 'hydro':
            units = ['1e9 cfs', 'Billion acre-ft']
        else:
            units = ['GW', 'GWh']
        oom = oom - 6
        for f in list(data.keys()):
            data[f] = [k / 1e6 for k in data[f]]
    elif oom > 3.30103:
        if net == 'hydro':
            units = ['1e6 cfs', 'Million acre-ft']
        else:
            units = ['MW', 'MWh']
        oom = oom - 3
        for f in list(data.keys()):
            data[f] = [k / 1e3 for k in data[f]]
    else:
        if net == 'hydro':
            units = ['1000 cfs', '1000 acre-ft']
        elif net == 'cold_water' or net == 'building_temperature':
            units = ['F', 'kWh']
        else:
            units = ['kW', 'kWh']
    if net == 'building_temperature':
        Ymax = 78
        Ymin = 56
        Yspace = 2
    else:
        if (
            oom - int(oom)
        ) == 0:  # count in increments of 1, 10, 100 or 1000 etc
            Yspace = 2.5 * 10 ** (oom - 1)
            Ymax = 10 ** oom
        elif (oom - int(oom)) > 0.6990:
            Yspace = 2.5 * 10 ** int(oom)
            Ymax = 10 ** int(1 + oom)
        elif (
            oom - int(oom)
        ) > 0.30103:  # count in increments of 5, 50, 500 or 5000 etc
            Yspace = 10 ** int(oom)
            Ymax = 0.5 * 10 ** int(1 + oom)
        else:  # count in increments of 2, 20, 200 or 2000 etc
            Yspace = 0.5 * 10 ** int(oom)
            Ymax = 0.2 * 10 ** int(1 + oom)

        negTicks = int(min(min(data[f]) for f in list(data.keys())) / Yspace)

        if negTicks >= 0:
            Ymin = 0
        else:
            Ymin = Yspace * negTicks
        nticks = int((Ymax - Ymin) / Yspace) + 1
        while nticks > 14:
            Yspace = 2 * Yspace
            nticks = int((Ymax - Ymin) / Yspace) + 1
            negTicks = int(
                min(min(data[f]) for f in list(data.keys())) / Yspace
            )
            Ymin = Yspace * negTicks

        Yticks = [Ymin + j * Yspace for j in range(nticks)]
    return data, units, Ymax, Ymin, Yticks


def assign_colors(n, cm_parula):
    n2 = len(cm_parula)
    color = []
    for i in range(n):
        v = i / n * n2
        r = v - int(v)
        color.append([
            (1 - r) * cm_parula[int(v)][j] + r * cm_parula[int(v + 0.5)][j]
            for j in range(3)
        ])
    return color


def convert_to_steps(date, original):
    names = list(original.keys())
    new = {}
    date_step = []
    for n in names:
        new[n] = []
        for t in range(len(date)):
            new[n].extend([original[n][t], original[n][t]])
    for t in range(len(date) - 1):
        date_step.extend([date[t], date[t + 1] - dt.timedelta(seconds=0.001)])

    date_step.append(date[-1])
    date_step.append(date[-1] + (date[-1] - date[-2]))
    return date_step, new
