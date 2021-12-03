# import matplotlib.axes as axes
import sys

import seaborn as sns


def hello_world():
    print("Hello World")


def fix_plot_axes(plot):
    plot.set_xlabel(fontdict=dict(weight='bold'), labelpad=10)
    plot.set_ylabel(fontdict=dict(weight='bold'), labelpad=10)
    plot.set_title(fontdict=dict(weight='bold'), fontsize=20, pad=20)


def sns_customise_theme(labelsize="default", labelpad="default", axeslabelweight='bold', fig_height = "default", fig_width="default", verbose = False):
    """
    :param labelsize: size of axis titles
    :param labelpad: padding between axis titles and figure
    :param axeslabelweight: axis title weight (e.g. 'bold' or 'normal')
    :param fig_height: width of the figure
    :param fig_width: height of the figure
    :param verbose: verobosity
    :return: NoneType
    """


    rcDict = {'axes.labelweight': axeslabelweight}

    if labelsize != "default":
        rcDict["axes.labelsize"] = labelsize

    if labelpad != "default":
        rcDict["axes.labelpad"] = labelpad

    if fig_height != "default" and fig_width != "default":
        rcDict["figure.figsize"] = (fig_height, fig_width)
    elif (fig_height != "default") + (fig_width != "default") == 1:
        print("fig_height and fig_width must BOTH be specified to change figsize")

    if(verbose):
        print(rcDict)

    sns.set_theme(rc=rcDict)

#For testing
#sns_theme_fav_1(fig_height=10, verbose = True); sns.displot(data=sns.load_dataset('iris'), x='sepal_width')