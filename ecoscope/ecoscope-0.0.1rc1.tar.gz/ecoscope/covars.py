import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn')


def plot_timeseries_ndvi_data(ndvi_data=None, output_fig='', title='', time_range=None):

    fig, ax = plt.subplots(figsize=(15, 7))
    sns.lineplot(x=ndvi_data.index,
                 y=ndvi_data['NDVI'],
                 color='navy',
                 linestyle='solid',
                 marker='o',
                 linewidth=1.0,
                 label='Current NDVI')

    sns.lineplot(x=ndvi_data.index,
                 y=ndvi_data['mean'],
                 color='g',
                 label='Historical Mean NDVI',
                 linewidth=2.0)

    ax.fill_between(x=ndvi_data.index,
                    y1=ndvi_data['mean'] - 2.0 * ndvi_data['std'],
                    y2=ndvi_data['mean'] + 2.0 * ndvi_data['std'],
                    alpha=0.1,
                    color='green',
                    label='95% CI')

    ax.set_xlim(time_range[0], time_range[1]) if time_range else None
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    ax.set_ylim(0.0, 1)
    ax.grid(True)
    ax.set_ylabel('NDVI')
    ax.set_xlabel('Time')
    ax.set_title(title)
    ax.legend()

    plt.xticks(rotation=90)
    fig.autofmt_xdate()

    fig.savefig(output_fig) if output_fig != '' else None
    return fig, ax
