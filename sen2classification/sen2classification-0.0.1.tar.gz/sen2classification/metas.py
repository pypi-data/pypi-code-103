import copy

import rasterio


class Meta:
    '''Class for creating metadata for raster image.

    Attributes
    ----------
    input_raster : str
        raster file path
    default_meta : dict
        sentinel 2 default metadata

    Methods
    -------
    set_default_meta()
        sets default metadata
    '''

    def __init__(self, input_raster: str) -> None:
        self.input_raster = input_raster
        self.default_meta = self.set_default_meta()

    def set_default_meta(self):
        with rasterio.open(self.input_raster) as src:
            meta = copy.deepcopy(src.meta)
            # Driver is changed to Gtiff because it is more widely used format
            meta['driver'] = 'Gtiff'
            return meta

    def get_meta(self):
        pass


class ResampledMeta(Meta):
    '''Metadata for resampled raster image.

    Methods
    -------
    get_meta()
        returns metadata

    '''

    def __init__(self, input_raster) -> None:
        super().__init__(input_raster)

    def get_meta(self) -> dict:
        return self.default_meta


class SpectralIndexMeta(Meta):
    '''Spectral index raster image metadata.

    Methods
    -------
    get_meta()
        returns metadata
    '''

    def __init__(self, input_raster) -> None:
        super().__init__(input_raster)

    def get_meta(self) -> dict:
        self.default_meta['dtype'] = 'float32'
        self.default_meta['nodata'] = 99999
        return self.default_meta


class LandCoverMeta(Meta):
    '''Land cover raster image metadata.

    Methods
    -------
    get_meta()
        returns metadata
    '''

    def __init__(self, input_raster) -> None:
        super().__init__(input_raster)

    def get_meta(self) -> dict:
        self.default_meta['dtype'] = 'uint8'
        self.default_meta['nodata'] = 0
        return self.default_meta


class KmeansMeta(Meta):
    '''K means raster image metadata.

    Methods
    -------
    get_meta()
        returns metadata

    '''

    def __init__(self, input_raster) -> None:
        super().__init__(input_raster)

    def get_meta(self) -> dict:
        self.default_meta['dtype'] = 'uint8'
        return self.default_meta
