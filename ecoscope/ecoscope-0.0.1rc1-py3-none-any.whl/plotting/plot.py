import typing

import geopandas
import mapclassify
import pandas
import itertools
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns
from shapely.geometry import MultiLineString
from ecoscope.plotting import GEOMAP

ESRI_TOPOLOGY_BASEMAP = 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}'


class SPEEDMAP(GEOMAP):
    speedmap_labels = []

    @property
    def default_speed_color(self):
        return ['#1a9850', '#91cf60', '#d9ef8b', '#fee08b', '#fc8d59', '#d73027']

    @staticmethod
    def _speedmap_labels(bins):
        return [f'{bins[i]:.1f} - {bins[i + 1]:.1f} km/hr' for i in range(len(bins) - 1)]

    @property
    def classification_methods(self):
        return {
            "equal_interval": mapclassify.EqualInterval,
            "natural_breaks": mapclassify.NaturalBreaks,
            "quantile": mapclassify.Quantiles,
            "std_mean": mapclassify.StdMean,
            "max_breaks": mapclassify.MaximumBreaks,
            "fisher_jenks": mapclassify.FisherJenks,
        }

    @staticmethod
    def create_multi_linestring(s):
        return MultiLineString(s['geometry'].tolist())

    def apply_classification(self, x, k, cls_method='natural_breaks', multiples=None):
        """
        Function to select which classifier to apply to the speed distributed data.

        Args:
        __________
        x (array)          : The input array to be classified. Must be 1-dimensional
        k (int)            : Number of classes required.
        cls_method (str)   : Classification method
        multiples (array)  : the multiples of the standard deviation to add/subtract from
                             the sample mean to define the bins.
                             defaults=[-2,-1,1,2]
        """
        if multiples is None:
            multiples = [-2, -1, 1, 2]

        classifier = self.classification_methods.get(cls_method)
        if not classifier:
            return

        map_classifier = classifier(x, multiples) if cls_method == 'std_mean' else classifier(x, k)
        edges, _, _ = mapclassify.classifiers._format_intervals(map_classifier, fmt="{:.2f}")

        print(map_classifier)
        return [float(i) for i in edges]

    def create_speedmap_df(self,
                           multi_trajectory: geopandas.GeoDataFrame,
                           classification_method: str = 'equal_interval',
                           no_class: int = 6,
                           speed_colors: typing.List = None
                           ):
        if speed_colors is None:
            speed_colors = self.default_speed_color[:no_class]

        # apply classification on speed data.
        bins = self.apply_classification(multi_trajectory.speed_kmhr, no_class, cls_method=classification_method)
        multi_trajectory['speed_colour'] = pandas.cut(x=multi_trajectory.speed_kmhr,
                                                      bins=bins, labels=speed_colors,
                                                      include_lowest=True)
        # Group the data according to speed and create multi-linestrings for each group
        speedmap_df = geopandas.GeoDataFrame(geometry=multi_trajectory.groupby('speed_colour').apply(
            self.create_multi_linestring), crs=4326).reset_index()

        speedmap_df.sort_values(by='speed_colour', inplace=True)
        self.speedmap_labels = self._speedmap_labels(bins)
        return speedmap_df

    def _add_layers(self, df, basemap, linewidth):
        self.add_tiled_layer(source=basemap, crs=df.crs)
        self.add_vector_layer(df,
                              color=df.speed_colour.unique(),
                              column='speed_colour',
                              linewidth=linewidth,
                              linestyle='-', marker=0,
                              label=self.speedmap_labels)

    def plot_speedmap(self,
                      multi_trajectory: geopandas.GeoDataFrame,
                      basemap=ESRI_TOPOLOGY_BASEMAP,
                      classification_method: str = 'equal_interval',
                      linewidth: float = 1.,
                      no_class: int = 6,
                      speed_colors: typing.List = None,
                      **kwargs: typing.Any
                      ):

        df = self.create_speedmap_df(multi_trajectory=multi_trajectory,
                                     classification_method=classification_method,
                                     no_class=no_class,
                                     speed_colors=speed_colors)
        self._add_layers(df=df, basemap=basemap, linewidth=linewidth)
        return super(SPEEDMAP, self).plot(**kwargs)


# alias
SpeedMap = SPEEDMAP


def timeseries(df,
               x='x',
               y='y',
               xlabel='',
               ylabel='y',
               title='',
               legend_label='',
               fmt='g',
               figsize=(15, 7),
               linestyle='solid'):
    fig, ax = plt.subplots(figsize=figsize)
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.grid(True)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.plot_date(df[x], df[y], fmt=fmt, label=legend_label, linewidth=1.5, linestyle=linestyle)
    fig.autofmt_xdate()
    ax.legend(loc=0)
    return fig, ax


def datacount(data, grouping_column, figsize=(20, 10), title='', xlabel=None, ylabel=None, rotation=90, **countplot):
    sns.set(rc={'figure.figsize': figsize})
    ax = sns.countplot(x=grouping_column, data=data, **countplot)
    plt.xticks(rotation=rotation)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return ax


def seasonal_window(data,
                    x='start',
                    y='season_code',
                    xlabel='',
                    ylabel='Season (1=wet, 0=dry)',
                    draw_style='steps-post',
                    step='post',
                    color='blue',
                    alpha=0.3):
    ax = sns.lineplot(x=x, y=y, data=data, drawstyle=draw_style)
    l1 = ax.lines[0]
    x1 = l1.get_xydata()[:, 0]
    y1 = l1.get_xydata()[:, 1]
    ax.fill_between(x1, y1, step=step, color=color, alpha=alpha)
    ax.set(xlabel=xlabel, ylabel=ylabel)
    return ax


def ndvi_seasonal_transition(vals,
                             season_cut_values,
                             xlabel='',
                             ylabel='',
                             title='',
                             subplot_kwargs=None,
                             histplot_kwargs=None,
                             axvline_kwargs=None):
    xmin = min(vals) - 0.1 * min(vals)
    xmax = max(vals) + 0.1 * min(vals)
    fig, ax = plt.subplots(**subplot_kwargs)
    ax.set_xlim(xmin, xmax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    sns.histplot(vals, **histplot_kwargs, ax=ax)
    [ax.axvline(x=i, **axvline_kwargs) for i in season_cut_values[1:-1]]
    return ax
