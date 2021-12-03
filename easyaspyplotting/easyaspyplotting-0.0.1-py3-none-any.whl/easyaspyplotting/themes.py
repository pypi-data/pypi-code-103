# import matplotlib.axes as axes
import seaborn as sns


def hello_world():
    print("Hello World")


def fix_plot_axes(plot):
    plot.set_xlabel(fontdict=dict(weight='bold'), labelpad=10)
    plot.set_ylabel(fontdict=dict(weight='bold'), labelpad=10)
    plot.set_title(fontdict=dict(weight='bold'), fontsize=20, pad=20)


def sns_theme_fav_1(labelsize=10.0, labelpad=13, axeslabelweight='bold'):
    """
    :param labelsize: size of axis titles
    :param labelpad: padding between axis titles and figure
    :param axeslabelweight: axis title weight (e.g. 'bold' or 'normal')
    :return: NoneType
    """
    sns.set_theme(rc={'axes.labelsize': labelsize, 'axes.labelpad': labelpad, 'axes.labelweight': axeslabelweight})
