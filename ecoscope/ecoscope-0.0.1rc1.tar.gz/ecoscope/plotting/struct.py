import uuid

import rasterio
from boltons.dictutils import OrderedMultiDict


class LAYERS(OrderedMultiDict):

    def __init__(self, *args, **kwargs):
        super(LAYERS, self).__init__()
        self._clear_ll()

    @property
    def uuid(self):
        return str(uuid.uuid4())

    def tiled_layer(self, source, **plot_kwargs):
        vis_props = dict(source=source, properties=plot_kwargs)
        self.add(f'tiled_layer_{self.uuid}', vis_props)

    def vector_layer(self, geo_dataframe, **plot_kwargs):
        vis_props = dict(df=geo_dataframe, properties=plot_kwargs)
        self.add(f'geo_dataframe_{self.uuid}', vis_props)

    def raster_layer(self, raster_path, resampling=rasterio.enums.Resampling.bilinear, crs=None, **plot_kwargs):
        vis_props = dict(raster=raster_path, resampling=resampling, crs=crs, properties=plot_kwargs)
        self.add(f'raster_layer_{self.uuid}', vis_props)
