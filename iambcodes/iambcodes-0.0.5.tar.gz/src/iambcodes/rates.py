import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting._matplotlib.style import get_standard_colors


def plot_multi(data, cols=None, spacing=.1, **kwargs):
# source:
# https://stackoverflow.com/questions/11640243/pandas-plot-multiple-y-axes

    # Get default color style from pandas - can be changed to any other color list
    if cols is None: cols = data.columns
    if len(cols) == 0: return
    colors = get_standard_colors(num_colors=len(cols))

    fig, ax = plt.subplots()
    # First axis
    ax.plot(data.loc[:, cols[0]].values, data.loc[:, cols[1]].values, **kwargs)
#    ax = data.loc[:, cols[0]].plot(label=cols[0], color=colors[0], **kwargs)
    ax.set_ylabel(ylabel=cols[1])
    lines, labels = ax.get_legend_handles_labels()

    for n in range(2, len(cols)):
        # Multiple y-axes
        ax_new = ax.twinx()
        ax_new.spines['right'].set_position(('axes', 1 + spacing * (n - 1)))
        data.loc[:, cols[n]].plot(ax=ax_new, label=cols[n], color=colors[n % len(colors)], **kwargs)
        ax_new.set_ylabel(ylabel=cols[n])
        
        # Proper legend position
        line, label = ax_new.get_legend_handles_labels()
        lines += line
        labels += label
        
    ax.legend(lines, labels, loc=0)
    return ax


def SubVector(StartEnd, Vector):
    '''
    Extract a sub-vector based on start and end values. The output are the indices in the input vector.
    '''
    Above = Vector >= StartEnd[0]
    Below = Vector < StartEnd[1]
    Select = np.logical_and(Above, Below)
    return np.arange(len(Vector))[Select]
    