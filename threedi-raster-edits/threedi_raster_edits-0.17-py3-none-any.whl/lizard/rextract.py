# -*- coding: utf-8 -*-
# (c) Nelen & Schuurmans, see LICENSE.rst.
"""
Rextract, the king of extractors.
Extract parts of lizard rasters using geometries from a shapefile.
Please note that any information about the spatial reference system in the
shapefile is ignored.
If something goes wrong due to a problem on one of the lizard servers, it may
be possible to resume the process by keeping the output folder intact and
retrying exactly the same command.

from raster-tools


Note:
    
    Threading is faster but can be more buggy, not all comments are printed as they should.
    Files are kept to capture the progress
    
    
General todo is just keeping it steady
    
"""

# from http.client import responses
from time import sleep

import contextlib
import http
import pathlib
import requests
import uuid as uid
import numpy as np
import logging
import threading
import queue as queues
from osgeo import gdal
from datetime import datetime

from threedi_raster_edits.gis.dataset import Dataset
from threedi_raster_edits.gis.layer import Layer
from threedi_raster_edits.gis.geotransform import GeoTransform
from threedi_raster_edits.utils.progress import Progress


MAX_THREADS = 1  # if set to 0 there will be no limit on the amount of threads

# urls and the like
API_URL = "https://%s.lizard.net/api/v4/rasters/"

# gdal drivers and options
MEM_DRIVER = gdal.GetDriverByName("mem")
TIF_DRIVER = gdal.GetDriverByName("gtiff")
TIF_OPTIONS = [
    "TILED=YES",
    "BIGTIFF=YES",
    "SPARSE_OK=TRUE",
    "COMPRESS=DEFLATE",
]

# dtype argument lookups
DTYPES = {
    "u1": gdal.GDT_Byte,
    "u2": gdal.GDT_UInt16,
    "u4": gdal.GDT_UInt32,
    "i2": gdal.GDT_Int16,
    "i4": gdal.GDT_Int32,
    "f4": gdal.GDT_Float32,
}

# argument defaults
TIMESTAMP = "1970-01-01T00:00:00Z"
ATTRIBUTE = "name"
SRS = "EPSG:28992"
CELLSIZE = 0.5
DTYPE = "f4"
SUBDOMAIN = "demo"
FILL_VALUE = -9999

# sleep and retry
STATUS_RETRY_SECONDS = {
    http.HTTPStatus.SERVICE_UNAVAILABLE: 10,
    http.HTTPStatus.GATEWAY_TIMEOUT: 0,
}
RETRY_SLEEP = 10
INTER_REQUEST_SLEEP = 2
AUTH = {}

# logging

logger = logging.getLogger(__name__)


def set_api_key(api_key):
    AUTH["api_key"] = api_key


def get_api_key():
    return AUTH["api_key"]


class Indicator:
    def __init__(self, path):
        self.path = str(path)

    def get(self):
        try:
            with open(self.path) as f:
                return int(f.read())
        except IOError:
            return 0

    def set(self, value):
        with open(self.path, "w") as f:
            f.write("%s\n" % value)

    def append(self, value, do_print=True):
        if do_print:
            print("\r" + value, flush=True)
        with open(self.path, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {value}\n")


class Index:
    """Iterates the indices into the target dataset."""

    def __init__(self, dataset, geometry, api_key):
        """
        Rasterize geometry into target dataset extent to find relevant
        blocks.
        """
        width, height = dataset.GetRasterBand(1).GetBlockSize()
        geo_transform = GeoTransform(dataset.GetGeoTransform())

        # create an array in which each cell represents a dataset block
        shape = (
            (dataset.RasterYSize - 1) // height + 1,
            (dataset.RasterXSize - 1) // width + 1,
        )
        index = np.zeros(shape, dtype="u1")
        kwargs = {
            "geotransform": geo_transform.scaled(width, height),
            "spatial_reference": dataset.GetProjection(),
        }

        # find active blocks by rasterizing geometry
        options = ["all_touched=true"]
        with Layer(geometry) as layer:
            with Dataset(index[np.newaxis], **kwargs) as ds_idx:
                gdal.RasterizeLayer(
                    ds_idx,
                    [1],
                    layer,
                    burn_values=[1],
                    options=options,
                )

        # store as attributes
        self.block_size = width, height
        self.dataset_size = dataset.RasterXSize, dataset.RasterYSize
        self.geo_transform = geo_transform
        self.indices = index.nonzero()
        self.api_key = api_key

    def _get_indices(self, serial):
        """Return indices into dataset."""
        block_width, block_height = self.block_size
        ds_width, ds_height = self.dataset_size
        y, x = self.indices[0][serial].item(), self.indices[1][serial].item()
        x1 = block_width * x
        y1 = block_height * y
        x2 = min(ds_width, (x + 1) * block_width)
        y2 = min(ds_height, (y + 1) * block_height)
        return x1, y1, x2, y2

    def _get_bbox(self, indices):
        """Return bbox tuple for a rectangle."""
        u1, v1, u2, v2 = indices
        p, a, b, q, c, d = self.geo_transform
        x1 = p + a * u1 + b * v1
        y2 = q + c * u1 + d * v1
        x2 = p + a * u2 + b * v2
        y1 = q + c * u2 + d * v2
        return "%s,%s,%s,%s" % (x1, y1, x2, y2)

    def __len__(self):
        return len(self.indices[0])

    def get_chunks(self, start=1):
        """
        Return chunk generator.
        Note that the serial number starts counting at 1.
        """
        for serial in range(start, len(self) + 1):
            x1, y1, x2, y2 = indices = self._get_indices(serial - 1)
            width, height, origin = x2 - x1, y2 - y1, (x1, y1)
            bbox = self._get_bbox(indices)
            yield Chunk(
                bbox=bbox,
                width=width,
                height=height,
                origin=origin,
                serial=serial,
                api_key=self.api_key,
            )


class Target:
    """
    Wraps the resulting gdal dataset.
    """

    def __init__(self, path, geometry, dtype, fillvalue, api_key, **kwargs):
        """Kwargs contain cellsize and uuid."""
        # coordinates
        self.geometry = geometry
        path = pathlib.Path(path)

        # types
        self.dtype = dtype
        if fillvalue is None:
            # pick the largest value possible within the dtype
            info = np.finfo if dtype.startswith("f") else np.iinfo
            self.fillvalue = info(dtype).max.item()
        else:
            # cast the string dtype to the correct python type
            self.fillvalue = np.dtype(self.dtype).type(fillvalue).item()

        # dataset
        print(path)
        if path.exists():
            print("Appending to %s... " % path, end="")
            self.dataset = gdal.Open(str(path), gdal.GA_Update)
        else:
            print("Creating %s" % path)
            self.dataset = self._create_dataset(path=str(path), **kwargs)

        # chunks
        self.index = Index(
            dataset=self.dataset, geometry=self.geometry, api_key=api_key
        )

    def __len__(self):
        return len(self.index)

    @property
    def data_type(self):
        return DTYPES[self.dtype]

    @property
    def no_data_value(self):
        return self.fillvalue

    @property
    def projection(self):
        return self.geometry.GetSpatialReference().ExportToWkt()

    def _create_dataset(self, path, cellsize, subdomain, time, uuid):
        """Create output tif dataset."""
        # calculate
        a, b, c, d = cellsize, 0.0, 0.0, -cellsize
        x1, x2, y1, y2 = self.geometry.GetEnvelope()
        p, q = a * (x1 // a), d * (y2 // d)

        width = -int((p - x2) // a)
        height = -int((q - y1) // d)
        geo_transform = p, a, b, q, c, d

        # create
        dataset = TIF_DRIVER.Create(
            path,
            width,
            height,
            1,
            self.data_type,
            options=TIF_OPTIONS,
        )
        dataset.SetProjection(self.projection)
        dataset.SetGeoTransform(geo_transform)
        dataset.GetRasterBand(1).SetNoDataValue(self.no_data_value)

        # meta
        dataset.SetMetadata(
            {"subdomain": subdomain, "time": time, "uuid": uuid},
        )

        return dataset

    def get_chunks(self, start):
        return self.index.get_chunks(start)

    def save(self, chunk):
        """ """
        # read and convert datatype
        with chunk.as_dataset() as dataset:
            band = dataset.GetRasterBand(1)
            active = band.GetMaskBand().ReadAsArray()[np.newaxis]
            array = band.ReadAsArray().astype(self.dtype)[np.newaxis]
        # determine inside pixels
        inside = np.zeros_like(active)
        kwargs = {
            "geotransform": dataset.GetGeoTransform(),
            "spatial_reference": dataset.GetProjection(),
        }
        with Layer(self.geometry) as layer:
            with Dataset(inside, **kwargs) as dataset:
                gdal.RasterizeLayer(dataset, [1], layer, burn_values=[255])

        # mask outide or inactive
        array[~np.logical_and(active, inside)] = self.no_data_value

        # write to target dataset
        kwargs.update(nodata_value=self.no_data_value)
        with Dataset(array, **kwargs) as dataset:
            data = dataset.ReadRaster(0, 0, chunk.width, chunk.height)
            args = chunk.origin + (chunk.width, chunk.height, data)
        self.dataset.WriteRaster(*args)


class Chunk:
    def __init__(self, bbox, width, height, origin, serial, api_key):
        # for request
        self.bbox = bbox
        self.width = width
        self.height = height

        # for result
        self.origin = origin
        self.serial = serial

        # the geotiff data
        self.response = None
        self.api_key = api_key

    def fetch(self, subdomain, uuid, time, srs, retries, chunk_log):
        request = {
            "url": API_URL % subdomain + uuid + "/data/",
            "params": {
                "start": time,
                "bbox": self.bbox,
                "projection": srs,
                "width": self.width,
                "height": self.height,
                "format": "geotiff",
            },
        }
        # add retries
        succes = False
        max_retries_reached = False
        retry = 0
        while not succes and not max_retries_reached:
            try:
                # response is not 200 is an external error
                # respose gives exceptions is an internal (own pc/server) error

                self.response = requests.get(**request, auth=("__key__", self.api_key))
                succes = self.response.status_code == 200
                # chunk_log.append(self.response.url, False)
                internal_exception = False
            except Exception as e:
                chunk_log.append(f"Found exception {e}")
                succes = False
                internal_exception = True

            retry += 1
            max_retries_reached = retry == retries

            if not succes:
                chunk_log.append(
                    f"Retrying after {RETRY_SLEEP} seconds {retry}/{retries}"
                )
                if internal_exception:
                    chunk_log.append(
                        "What are you doing, are you even connected to the internet?"
                    )
                sleep(RETRY_SLEEP)

        if not succes and max_retries_reached:
            chunk_log.append(
                """Cannot succesfully get a block, most likely an
                  internet or lizard error. FIX IT YO (-.-), Bye bye, im out...""",
                True,
            )
            sleep(30)
            return

    @contextlib.contextmanager
    def as_dataset(self):
        """Temporily serve data as geotiff file in virtual memory."""
        mem_file = f"/vsimem/{uid.uuid4()}.tif"
        gdal.FileFromMemBuffer(mem_file, self.response.content)
        yield gdal.Open(mem_file)


def filler(queue, chunks, **kwargs):
    """Fill queue with chunks from batch and terminate with None."""
    for chunk in chunks:
        thread = threading.Thread(target=chunk.fetch, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        queue.put((thread, chunk))
    queue.put(None)


class RasterExtraction:
    """
     Represent the extraction of a single geometry.

     Recommended code to use rextract in python is as follows:
         rextract = RasterExtraction(PASSWORD, quiet=False)
         rextract.run(path, uuid, geometry, time=TIMESTAMP, cellsize=CELLSIZE, threads=1)

     One can also use rextract in a loop as follows:
         rextract = RasterExtraction(PASSWORD, quiet=False)
         rextract.set_variables(path, UUID, geometry)
         rextract.threads = 2
         for progress in rextract:
             print(progress)

    Pprogress is then returned as a counter which is usefull for qgis .

    Note that one can vary threads, depending on the amount of threads a different
    method is chosen. While one can use threading with a n=1, it is chosen here not to.
    This is due to the fact that we want one different method here as a backup.

    """

    def __init__(
        self,
        api_key,
        srs="EPSG:28992",
        retries=100,
        subdomain=SUBDOMAIN,
        quiet=False,
        fillvalue=FILL_VALUE,
        dtype=DTYPE,
        inter_request_sleep=INTER_REQUEST_SLEEP,
    ):

        self.srs = srs
        self.subdomain = subdomain
        self.retries = retries
        self.quiet = quiet
        self.fillvalue = fillvalue
        self.dtype = dtype
        self.inter_request_sleep = inter_request_sleep
        self.api_key = api_key

        self.check_login(subdomain)
        self._threads = 1

    def __iter__(self):
        """iter is used especially for qgis to provide feedback on the process and download at the same time"""
        self.generate_output()
        total = len(self.target)
        completed = self.progress()

        if self.threads > 4:
            self.rextract_log.append(f"Set maximum threads to: len({self.threads})")
            self.threads = 4

        if self.threads < 2:
            self.single = True
            self.rextract_log.append("Using single thread")
        else:
            self.single = False
            self.rextract_log.append(f"Using multiple threads: {self.threads}")

        queue = queues.Queue(maxsize=self.threads - 1)

        self.indicator.set(completed)
        chunk_factory = self.target.get_chunks(start=completed + 1)
        fetch_kwargs = {
            "chunks": chunk_factory,
            "subdomain": self.subdomain,
            "uuid": self.uuid,
            "time": self.time,
            "srs": self.srs,
            "retries": self.retries,
            "queue": queue,
            "chunk_log": self.rextract_log,
        }

        if self.single:
            del fetch_kwargs["queue"]
            del fetch_kwargs["chunks"]

            for chunk in Progress(chunk_factory, "Rextract", self.quiet, total=total):
                chunk.fetch(**fetch_kwargs)
                self.target.save(chunk)
                sleep(self.inter_request_sleep)
                completed = chunk.serial
                self.indicator.set(completed)
                yield (completed / total) * 100
        else:
            filler_thread = threading.Thread(target=filler, kwargs=fetch_kwargs)
            filler_thread.daemon = False
            filler_thread.start()
            pbar = Progress(message="Rextract", total=total, quiet=self.quiet)
            while True:
                # fetch loaded chunks
                try:
                    fetch_thread, chunk = queue.get()
                    fetch_thread.join()  # this makes sure the chunk is loaded
                except TypeError:
                    self.indicator.set(completed)
                    break

                # save the chunk to the target
                self.target.save(chunk)
                self.indicator.set(completed)

                completed = chunk.serial
                pbar.update()
                progress = (completed / total) * 100

                if progress == 100:
                    filler_thread.join()

                yield progress
        self.target = None

    @property
    def threads(self):
        return self._threads

    @threads.setter
    def threads(self, value):
        self._threads = value

    def set_variables(self, path, uuid, geometry, cellsize=CELLSIZE, time=TIMESTAMP):
        self.path = path
        self.uuid = uuid
        self.cellsize = cellsize
        self.geometry = geometry
        self.time = time

    def generate_output(self):
        """generates a tiff and provides the indicator"""

        kwargs = {
            "uuid": self.uuid,
            "time": self.time,
            "cellsize": self.cellsize,
            "subdomain": self.subdomain,
        }

        self.target = Target(
            self.path, self.geometry, self.dtype, self.fillvalue, self.api_key, **kwargs
        )
        self.indicator = Indicator(path=self.path.replace(".tif", ".pro"))
        self.rextract_log = Indicator(path=self.path.replace(".tif", ".rextract_info"))
        self.rextract_log.append(f"Settings: {kwargs}")

    def progress(self):
        completed = self.indicator.get()

        total = len(self.target)
        if completed == total:
            self.rextract_log.append("Already complete.")
            return
        if completed > 0:
            self.rextract_log.append("Resuming from chunk %s." % completed)
        else:
            self.rextract_log.append(
                "Starting rextract from the beginning. Check your progress in .pro"
            )

        return completed

    def run(self, path, uuid, geometry, time=TIMESTAMP, cellsize=CELLSIZE, threads=1):
        self.threads = threads
        self.path = path
        self.uuid = uuid
        self.geometry = geometry
        self.cellsize = cellsize
        self.time = time
        self.cellsize = cellsize

        # go into the process of rextracting with a loop
        for progress in self:
            pass

    def check_login(self, subdomain):
        session = requests.Session()
        try:
            post = session.post(url=API_URL % subdomain, auth=("__key__", self.api_key))
            if post.text != "login-reg":
                print("Login successful")
            else:
                print(post.text)
        except Exception as e:
            print("Cannot login, not connected to the internet?", e)
            return

    # except Exception as e:
    #     print("Got Rextract exception: ", e)
    # finally:
    #     self.target = None
    #     print(f"Ended, written rextraction file to {path}")
