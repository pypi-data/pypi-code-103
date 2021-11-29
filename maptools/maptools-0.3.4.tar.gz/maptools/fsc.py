#
# Copyright (C) 2020 RFI
#
# Author: James Parkhurst
#
# This code is distributed under the GPLv3 license, a copy of
# which is included in the root directory of this package.
#
import logging
import numpy
import scipy.ndimage
import yaml
from matplotlib import pylab, ticker
from maptools.util import read, read_axis_order
from maptools.reorder import reorder
from math import sqrt


# Get the logger
logger = logging.getLogger(__name__)


def resolution_from_fsc(bins, fsc, value=0.5):
    """
    Compute the resolution from the FSC curve

    Args:
        bins (array): The resolution bins (ordered from low resolution to high)
        fsc (array): The fsc in that resolution bin

    Returns:
        (bin index, bin value, fsc value)

    """
    assert len(bins) == len(fsc)
    bin_index = len(bins) - 1
    bin_value = bins[bin_index]
    fsc_value = fsc[bin_index]
    for i, (b, f) in enumerate(zip(bins, fsc)):
        if f < 0.5:
            bin_index = i
            bin_value = b
            fsc_value = f
            break
    return bin_index, bin_value, fsc_value


def array_fsc(
    data1,
    data2,
    nbins=20,
    resolution=None,
    voxel_size=(1, 1, 1),
    axis=None,
    method="binned",
    **kwargs
):
    """
    Compute the local FSC of the map

    Args:
        data1 (array): The input map 1
        data2 (array): The input map 2
        nbins (int): The number of bins
        resolution (float): The resolution limit
        axis (tuple): The axis of the plane to compute the FSC
        method (str): Method to use (binned or averaged)

    Returns:
        array: The FSC

    """
    # Check the axis
    if type(axis) in [int, float]:
        axis = (axis,)

    # Get the subset of data
    logger.info("Computing FSC")

    # Average along the remaining axes
    if axis is not None:
        assert all(a in (0, 1, 2) for a in axis)
        voxel_size = tuple(voxel_size[a] for a in axis)
        axis = tuple(set((0, 1, 2)).difference(axis))
        data1 = numpy.mean(data1, axis=axis)
        data2 = numpy.mean(data2, axis=axis)

    # Check voxel size
    voxel_size = tuple(v if v > 0 else 1 for v in voxel_size)

    # Normalize the data
    data1 = (data1 - numpy.mean(data1)) / numpy.std(data1)
    data2 = (data2 - numpy.mean(data2)) / numpy.std(data2)

    # Compute the radius
    shape = data1.shape
    indices = [
        (1 / v) * (numpy.arange(s) - s // 2) / s for s, v in zip(shape, voxel_size)
    ]
    R = numpy.fft.fftshift(
        numpy.sum(numpy.array(numpy.meshgrid(*indices, indexing="ij")) ** 2, axis=0)
    )

    # Compute the FFT of the data
    X = numpy.fft.fftn(data1)
    Y = numpy.fft.fftn(data2)

    # Flatten the array
    X = X.flatten()
    Y = Y.flatten()
    R = R.flatten()

    # Get the max resolution
    max_resolution = 1.0 / sqrt(R.max())

    # Create a resolution mask
    if resolution is not None:
        if resolution < max_resolution:
            resolution = max_resolution
        mask = R < 1.0 / resolution ** 2
        X = X[mask]
        Y = Y[mask]
        R = R[mask]
    else:
        resolution = max_resolution

    # Multiply X and Y together
    XX = numpy.abs(X) ** 2
    YY = numpy.abs(Y) ** 2
    XY = numpy.real(X * numpy.conj(Y))

    # Compute local variance and covariance by binning with resolution
    if method == "binned":
        bin_index = numpy.floor(nbins * R * resolution ** 2).astype("int32")
        N = numpy.bincount(bin_index)
        varX = numpy.bincount(bin_index, XX)
        varY = numpy.bincount(bin_index, YY)
        covXY = numpy.bincount(bin_index, XY)
    elif method == "averaged":
        bin_index = numpy.floor((sum(shape) // 2) * R * resolution ** 2).astype("int32")
        N = numpy.bincount(bin_index)
        varX = numpy.bincount(bin_index, XX)
        varY = numpy.bincount(bin_index, YY)
        covXY = numpy.bincount(bin_index, XY)
        N = scipy.ndimage.uniform_filter(N, size=nbins, mode="nearest")
        varX = scipy.ndimage.uniform_filter(varX, size=nbins, mode="nearest")
        varY = scipy.ndimage.uniform_filter(varY, size=nbins, mode="nearest")
        covXY = scipy.ndimage.uniform_filter(covXY, size=nbins, mode="nearest")
    else:
        raise RuntimeError('Expected "binned" or "averaged", got %s' % method)

    # Compute the FSC
    tiny = 1e-5
    mask = (varX > tiny) & (varY > tiny)
    fsc = numpy.zeros(covXY.shape)
    fsc[mask] = covXY[mask] / (numpy.sqrt(varX[mask]) * numpy.sqrt(varY[mask]))
    bins = (1 / resolution ** 2) * numpy.arange(1, covXY.size + 1) / (covXY.size)

    # Print some output
    logger.info("Resolution, FSC")
    for b, f in zip(bins, fsc):
        logger.info("%.2f, %.2f" % (1 / sqrt(b), f))

    # Return the fsc
    return bins, N, fsc


def mapfile_fsc(
    input_map_filename1,
    input_map_filename2,
    output_plot_filename=None,
    output_data_filename=None,
    nbins=20,
    resolution=None,
    axis=None,
    method="binned",
):
    """
    Compute the local FSC of the map

    Args:
        input_map_filename1 (str): The input map filename
        input_map_filename2 (str): The input map filename
        output_plot_filename (str): The output map filename
        output_data_filename (str): The output data filename
        nbins (int): The number of bins
        resolution (float): The resolution limit
        axis (tuple): The axis of the plane to compute the FSC
        method (str): Method to use (binned or averaged)

    """
    # Check the axis
    if axis is None or type(axis) == int:
        axis = [axis]
    elif axis[0] is None or type(axis[0]) == int:
        axis = [axis]

    # Open the input files
    infile1 = read(input_map_filename1)
    infile2 = read(input_map_filename2)

    # Get the data
    data1 = infile1.data
    data2 = infile2.data

    # Reorder data2 to match data1
    data1 = reorder(data1, read_axis_order(infile1), (0, 1, 2))
    data2 = reorder(data2, read_axis_order(infile2), (0, 1, 2))

    # Loop through all axes
    results = []
    for current_axis in axis:

        # Compute the FSC
        bins, num, fsc = array_fsc(
            data1,
            data2,
            voxel_size=tuple(infile1.voxel_size[a] for a in ["z", "y", "x"]),
            nbins=nbins,
            resolution=resolution,
            axis=current_axis,
            method=method,
        )

        # Compute the FSC average
        fsc_average = float(numpy.sum(num * fsc) / numpy.sum(num))
        logger.info("FSC average: %g" % fsc_average)

        # Compute the resolution
        bin_index, bin_value, fsc_value = resolution_from_fsc(bins, fsc)
        logger.info("Estimated resolution = %f A" % (1 / sqrt(bin_value)))

        # Write the results dictionary
        results.append(
            {
                "axis": current_axis,
                "table": {"bin": list(map(float, bins)), "fsc": list(map(float, fsc))},
                "resolution": {
                    "bin_index": int(bin_index),
                    "bin_value": float(bin_value),
                    "fsc_value": float(fsc_value),
                    "estimate": float(1 / sqrt(bin_value)),
                },
                "fsc_average": fsc_average,
            }
        )

    # Write the FSC curve
    if output_plot_filename is not None:
        fig, ax = pylab.subplots(figsize=(8, 6))
        for r in results:
            bins = r["table"]["bin"]
            fsc = r["table"]["fsc"]
            axis = r["axis"]
            resolution = r["resolution"]["bin_value"]
            if axis == None:
                axis == (0, 1, 2)
            ax.plot(r["table"]["bin"], r["table"]["fsc"], label="axis - %s" % str(axis))
            ax.set_xlabel("Resolution (A)")
            ax.set_ylabel("FSC")
            ax.set_ylim(0, 1)
            ax.axvline(resolution, color="black")
            ax.xaxis.set_major_formatter(
                ticker.FuncFormatter(
                    lambda x, p: "%.1f" % (1 / sqrt(x)) if x > 0 else None
                )
            )
        ax.legend()
        fig.savefig(output_plot_filename, dpi=300, bbox_inches="tight")
        pylab.close(fig)

    # Write a data file
    if output_data_filename is not None:
        with open(output_data_filename, "w") as outfile:
            yaml.safe_dump(results, outfile)

    # Return the results
    return results


def fsc(*args, **kwargs):
    """
    Compute the FSC of the map

    """
    if len(args) > 0 and type(args[0]) == "str" or "input_map_filename1" in kwargs:
        func = mapfile_fsc
    else:
        func = array_fsc
    return func(*args, **kwargs)
