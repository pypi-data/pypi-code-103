import copy
import warnings

import contextily
import numpy
import rasterio

from ecoscope.plotting.geo_util import warp


class PLOTACCESSORY:
    @classmethod
    def plot_vector_layer(cls, axis, dataframe, zorder, **plot_kwargs):
        column = plot_kwargs.pop('column', None)
        if column:
            # Todo: leverage on geopandas plot_dataframe method
            df = dataframe[[column, 'geometry']]
            df.set_index(column, inplace=True)

            _kwargs = copy.copy(plot_kwargs)
            labels = dict(zip(df.index.unique(), _kwargs.setdefault('label', [])))
            colors = dict(zip(df.index.unique(), _kwargs.setdefault('color', [])))

            if labels or colors:
                plot_kwargs.pop('label', None)
                plot_kwargs.pop('color', None)
                plot_kwargs.pop('column', None)
                return [geom.plot(ax=axis,
                                  color=colors.get(value),
                                  label=labels.get(value, ''),
                                  zorder=zorder, **plot_kwargs)
                        for value, geom in df.groupby(column) if not geom.is_empty.all()]
        return dataframe.plot(ax=axis, column=column, zorder=zorder, **plot_kwargs)

    @classmethod
    def plot_raster_layer(cls, axis, raster_path, zorder, crs, resampling, **raster_kwargs):
        with rasterio.open(raster_path) as src:
            dataset = src.read()
            transform = src.transform
            dataset[dataset == src.nodata] = numpy.nan
            bb = src.bounds
            extent = bb.left, bb.right, bb.bottom, bb.top

            # Warp
            if src.crs != crs and crs is not None:
                dataset, bounds, _ = warp(dataset, transform, src.crs, crs, resampling)
                extent = bounds.left, bounds.right, bounds.bottom, bounds.top
            dataset = dataset.transpose(1, 2, 0)

        # plotting
        if dataset.shape[2] == 1:
            dataset = dataset[:, :, 0]
        cmap = raster_kwargs.pop('cmap', 'RdYlGn_r')
        return axis.imshow(dataset, extent=extent, cmap=cmap, zorder=zorder, **raster_kwargs)

    @classmethod
    def plot_tiled_layer(cls, axis, source, crs, zorder, **cx_kwargs):
        try:
            return contextily.add_basemap(ax=axis, source=source, crs=crs, zorder=zorder, **cx_kwargs)
        except Exception as exc:
            warnings.warn(str(exc))


plot_vector_layer = PLOTACCESSORY.plot_vector_layer
plot_raster_layer = PLOTACCESSORY.plot_raster_layer
plot_tiled_layer = PLOTACCESSORY.plot_tiled_layer
