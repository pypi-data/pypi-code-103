import os
import typing

import matplotlib.pyplot as plt
from geopy.distance import great_circle
from matplotlib_scalebar.scalebar import ScaleBar

from ecoscope.plotting._accesory import plot_vector_layer, plot_raster_layer, plot_tiled_layer
from ecoscope.plotting.struct import LAYERS

plt.style.use('seaborn')


class GEOMIXIN:

    @staticmethod
    def add_scalebar(ax, **kwargs):
        minx, maxx, miny, maxy = ax.axis()
        midpoint = (miny + maxy) / 2
        p1, p2 = (midpoint, int(minx)), (midpoint, int(minx) + 1)
        dist = great_circle(p1, p2).m
        ax.add_artist(ScaleBar(dist, location=kwargs.get("scalebar_location", "lower right")))

    @staticmethod
    def add_north_arrow(ax):
        x, y, arrow_length = 0.05, 0.98, 0.04
        ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
                    arrowprops=dict(facecolor='black', width=5, headwidth=15),
                    ha='center', va='center', fontsize=20,
                    xycoords=ax.transAxes)

    @staticmethod
    def set_extent(extent, ax):
        # extent:  MaxX, MaxY, MinX, and MinY.
        xlim = ([extent[0], extent[2]])
        ylim = ([extent[1], extent[3]])
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

    @staticmethod
    def apply_extent_ratio(extent_ratio, ax):
        # minx, miny, maxx, maxy = total_bounds

        minx, maxx, miny, maxy = ax.axis()
        x = maxx - minx
        y = maxy - miny

        # x-dimension
        new_x = x * extent_ratio
        diff_x = new_x - x
        minx = minx - 0.5 * diff_x
        maxx = maxx + 0.5 * diff_x

        # y-dimension:
        new_y = y * extent_ratio
        diff_y = new_y - y
        miny = miny - 0.5 * diff_y
        maxy = maxy + 0.5 * diff_y

        xlim = ([minx, maxx])
        ylim = ([miny, maxy])

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)


class GEOMAPLAYERS(LAYERS):
    @property
    def layers(self):
        return self

    @property
    def add_vector_layer(self):
        return self.vector_layer

    @property
    def add_tiled_layer(self):
        return self.tiled_layer

    @property
    def add_raster_layer(self):
        return self.raster_layer


class GEOMAP(GEOMAPLAYERS, GEOMIXIN):
    def __init__(self,
                 title: typing.Optional[str] = '',
                 figsize: typing.Tuple[int, int] = (15, 15),
                 legend: bool = True,
                 north_arrow: bool = True,
                 scale_bar: bool = True,
                 extent_ratio: float = 1.,
                 extent: typing.List[float] = None,
                 crs: typing.Any = 4326
                 ):
        self.figure, self.axis = plt.subplots(1, figsize=figsize)
        self._title = title
        self._figsize = figsize
        self._legend = legend
        self._north_arrow = north_arrow
        self._scalebar = scale_bar
        self._extent = extent or []
        self._extent_ratio = extent_ratio
        self._crs = crs
        super(GEOMAP, self).__init__(title=title,
                                     figsize=figsize,
                                     legend=legend,
                                     north_arrow=north_arrow,
                                     scale_bar=scale_bar,
                                     extent_ratio=extent_ratio,
                                     extent=extent)
        if len(list(self._extent)) == 4:
            self.set_extent(self._extent, self.axis)
        self.axis.set_aspect('equal', adjustable='datalim', anchor='C')

    def _add_geoplot_elements(self, **kwargs: typing.Any):
        frameon = kwargs.get('frameon', True)
        legend_prop = {'size': kwargs.get('legend_fontsize', 18)}
        legend_location = kwargs.get('legend_location', 'best')
        title_fontdict = {'fontsize': kwargs.get('title_fontsize', 25),
                          'fontweight': kwargs.get('title_fontweight', 'medium')}

        if self._legend:
            self.axis.legend(prop=legend_prop, loc=legend_location, frameon=frameon)
        if self._north_arrow:
            self.add_north_arrow(self.axis)
        if self._scalebar:
            self.add_scalebar(self.axis, **kwargs)
        if self._title:
            self.axis.set_title(self._title, fontdict=title_fontdict)

    def _reset_extent_ratio(self):
        # Temporary-Fix: Render the figure in order to get the the auto-scaled x and y dimension.
        # This will be used to create basemap that will align with axis box.
        try:
            self.figure.canvas.print_figure('_xufgremdfdefs')
            os.remove('_xufgremdfdefs.png')
        except OSError:
            pass
        self.apply_extent_ratio(self._extent_ratio or 1.0, self.axis)

    def plot(self, *args, **kwargs):
        layers = self.layers.keys(multi=True)

        for index, layer in reversed(list(enumerate(layers, 1))):
            layer_props = self.layers[layer]
            plot_kwargs = layer_props.setdefault('properties', {})

            if 'geo_dataframe' in layer:
                plot_vector_layer(self.axis,
                                  dataframe=layer_props['df'],
                                  zorder=index, **plot_kwargs)
            if 'raster_layer' in layer:
                plot_raster_layer(self.axis,
                                  raster_path=layer_props['raster'],
                                  resampling=layer_props['resampling'],
                                  crs=layer_props['crs'],
                                  zorder=index, **plot_kwargs)
            if 'tiled_layer' in layer:
                self._reset_extent_ratio()
                plot_tiled_layer(axis=self.axis,
                                 source=layer_props['source'],
                                 crs=plot_kwargs.pop('crs', self._crs),
                                 zorder=index, **plot_kwargs)

        self._add_geoplot_elements(**kwargs)
        return self.axis, self.figure

    def savefig(self, fname, **kwargs):
        self.figure.savefig(fname=fname, **kwargs)
