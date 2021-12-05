import rasterio
from rasterio.vrt import WarpedVRT


def warp(img, transform, source_crs, crs, resampling):
    """
    Warp an image.
    """
    band, height, width = img.shape
    with rasterio.MemoryFile() as memfile:
        with memfile.open(
                driver="GTiff",
                height=height,
                width=width,
                count=band,
                dtype=str(img.dtype.name),
                crs=source_crs,
                transform=transform,
        ) as dataset:
            dataset.write(img)

        with memfile.open() as src:
            with WarpedVRT(src, crs=crs, resampling=resampling) as vrt:
                ds = vrt.read()
                bounds = vrt.bounds
                transform = vrt.transform

    return ds, bounds, transform
