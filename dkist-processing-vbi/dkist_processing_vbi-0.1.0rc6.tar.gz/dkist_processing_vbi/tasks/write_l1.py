from typing import Literal

import dkist_fits_specifications
from astropy.io import fits
from dkist_processing_common.models.constants import BudName
from dkist_processing_common.tasks.write_l1 import WriteL1Frame

import dkist_processing_vbi
from dkist_processing_vbi.models.spectral_line import VBI_SPECTRAL_LINES


class VbiWriteL1Frame(WriteL1Frame):
    def add_dataset_headers(
        self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]
    ) -> fits.Header:

        header["DNAXIS"] = 3  # spatial, spatial, temporal
        header["DAAXES"] = 2  # Spatial, spatial
        header["DEAXES"] = 1  # Temporal

        # ---Spatial 1---
        header["DNAXIS1"] = header["NAXIS1"]
        header["DTYPE1"] = "SPATIAL"
        header["DPNAME1"] = "helioprojective latitude"
        header["DWNAME1"] = "helioprojective latitude"
        header["DUNIT1"] = header["CUNIT1"]

        # ---Spatial 2---
        header["DNAXIS2"] = header["NAXIS2"]
        header["DTYPE2"] = "SPATIAL"
        header["DPNAME2"] = "helioprojective longitude"
        header["DWNAME2"] = "helioprojective longitude"
        header["DUNIT2"] = header["CUNIT2"]

        # ---Temporal---
        header["DNAXIS3"] = self.num_dsps_repeats
        header["DTYPE3"] = "TEMPORAL"
        header["DPNAME3"] = "time"
        header["DWNAME3"] = "time"
        header["DUNIT3"] = "s"
        # Temporal position in dataset
        header["DINDEX3"] = header["DSPSNUM"]

        # ---Wavelength Info---
        # Do we need to check that this has length == 1?
        spectral_line = [
            l for l in VBI_SPECTRAL_LINES if l.name == self.constants[BudName.spectral_line.value]
        ][0]
        header["WAVEMIN"] = spectral_line.wavemin
        header["WAVEMAX"] = spectral_line.wavemax
        header["WAVEBAND"] = spectral_line.name
        header["WAVEUNIT"] = -9  # nanometers
        header["WAVEREF"] = "Air"

        # ---Other info---
        header["LEVEL"] = 1
        header["HEADVERS"] = dkist_fits_specifications.__version__
        header["CALVERS"] = dkist_processing_vbi.__version__
        header["INFO_URL"] = ""  # TODO: Need a link to put in here
        header["HEAD_URL"] = ""  # TODO: Put link here
        header["CAL_URL"] = ""  # TODO: DON'T put a link here                (just kidding, do it!)

        # Binning headers
        header["NBIN1"] = 1
        header["NBIN2"] = 1
        header["NBIN3"] = 1
        header["NBIN"] = header["NBIN1"] * header["NBIN2"] * header["NBIN3"]

        return header
