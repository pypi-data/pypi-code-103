import numpy as np

import numba
from numba import cuda

@numba.jit
def bin_2d(x, y, xmin=0, xmax=4096, ymin=0, ymax=4096):
    """  Bin XY position into 2d grid and throw away data outside the limits.

    Args:
        x (np.ndarray): X positions
        y (np.ndarray): Y positions
        xmin (int): minimum X value of the grid
        xmax (int): maximum X value of the grid
        ymin (int): minimum Y value of the grid
        ymax (int): maximum Y value of the grid

    Returns:
        np.ndarray: binned XY positions
    """
    grid = np.zeros((ymax - ymin, xmax - xmin), dtype=np.int32)

    valid_idx = np.logical_and(x >= xmin, y >= ymin)
    valid_idx = np.logical_and(valid_idx, y < ymax)
    valid_idx = np.logical_and(valid_idx, x < xmax)
    x = x[valid_idx]
    y = y[valid_idx]
    for xx, yy in zip(x, y):
        grid[int(yy), int(xx)] += 1
    return grid

@numba.jit(nopython=True)
def compute_bin(x, n, xmin, xmax):
    # special case to mirror NumPy behavior for last bin
    if x == xmax:
        return n - 1 # a_max always in last bin

    # SPEEDTIP: Remove the float64 casts if you don't need to exactly reproduce NumPy
    bin = np.int32(n * (np.float64(x) - np.float64(xmin)) / (np.float64(xmax) - np.float64(xmin)))

    if bin < 0 or bin >= n:
        return None
    else:
        return bin

@cuda.jit
def histogram(x, xmin, xmax, histogram_out):
    nbins = histogram_out.shape[0]
    bin_width = (xmax - xmin) / nbins

    start = cuda.grid(1)
    stride = cuda.gridsize(1)

    for i in range(start, x.shape[0], stride):
        # note that calling a numba.jit function from CUDA automatically
        # compiles an equivalent CUDA device function!
        bin_number = compute_bin(x[i], nbins, xmin, xmax)

        if bin_number >= 0 and bin_number < histogram_out.shape[0]:
            cuda.atomic.add(histogram_out, bin_number, 1)

@cuda.jit
def histogram2d(x, y, xmin, xmax, ymin, ymax, histogram_out):
    nbinsx = histogram_out.shape[1]
    nbinsy = histogram_out.shape[0]
    bin_widthx = (xmax - xmin) / nbinsx
    bin_widthy = (ymax - ymin) / nbinsy

    start = cuda.grid(1)
    stride = cuda.gridsize(1)

    for i in range(start, x.shape[0], stride):
        # note that calling a numba.jit function from CUDA automatically
        # compiles an equivalent CUDA device function!
        bin_numberx = compute_bin(x[i], nbinsx, xmin, xmax)
        bin_numbery = compute_bin(y[i], nbinsx, xmin, xmax)

        if bin_numberx >= 0 and bin_numberx < histogram_out.shape[1] and bin_numbery>=0 and bin_numbery<histogram_out.shape[0]:
            cuda.atomic.add(histogram_out, bin_number, 1)


@cuda.jit
def min_max(x, min_max_array):
    nelements = x.shape[0]

    start = cuda.grid(1)
    stride = cuda.gridsize(1)

    # Array already seeded with starting values appropriate for x's dtype
    # Not a problem if this array has already been updated
    local_min = min_max_array[0]
    local_max = min_max_array[1]

    for i in range(start, x.shape[0], stride):
        element = x[i]
        local_min = min(element, local_min)
        local_max = max(element, local_max)

    # Now combine each thread local min and max
    cuda.atomic.min(min_max_array, 0, local_min)
    cuda.atomic.max(min_max_array, 1, local_max)


def dtype_min_max(dtype):
    '''Get the min and max value for a numeric dtype'''
    if np.issubdtype(dtype, np.integer):
        info = np.iinfo(dtype)
    else:
        info = np.finfo(dtype)
    return info.min, info.max


@numba.jit(nopython=True)
def get_bin_edges(a, nbins, a_min, a_max):
    bin_edges = np.empty((nbins+1,), dtype=np.float64)
    delta = (a_max - a_min) / nbins
    for i in range(bin_edges.shape[0]):
        bin_edges[i] = a_min + i * delta

    bin_edges[-1] = a_max  # Avoid roundoff error on last point
    return bin_edges


def numba_gpu_histogram(a, bins):
    # Move data to GPU so we can do two operations on it
    a_gpu = cuda.to_device(a)

    ### Find min and max value in array
    dtype_min, dtype_max = dtype_min_max(a.dtype)
    # Put them in the array in reverse order so that they will be replaced by the first element in the array
    min_max_array_gpu = cuda.to_device(np.array([dtype_max, dtype_min], dtype=a.dtype))
    min_max[64, 64](a_gpu, min_max_array_gpu)
    a_min, a_max = min_max_array_gpu.copy_to_host()

    # SPEEDTIP: Skip this step if you don't need to reproduce the NumPy histogram edge array
    bin_edges = get_bin_edges(a, bins, a_min, a_max) # Doing this on CPU for now

    ### Bin the data into a histogram 
    histogram_out = cuda.to_device(np.zeros(shape=(bins,), dtype=np.int32))
    histogram[64, 64](a_gpu, a_min, a_max, histogram_out)

    return histogram_out.copy_to_host(), bin_edges


@numba.njit(nogil=True, parallel=False)
def hist2d_numba_seq(tracks, bins, ranges):
    H = np.zeros((bins[0], bins[1]), dtype=np.uint64)
    delta = 1 / ((ranges[:, 1] - ranges[:, 0]) / bins)

    for t in range(tracks.shape[1]):
        i = (tracks[0, t] - ranges[0, 0]) * delta[0]
        j = (tracks[1, t] - ranges[1, 0]) * delta[1]
        if 0 <= i < bins[0] and 0 <= j < bins[1]:
            H[int(i), int(j)] += 1

    return H

if __name__ == "__main__":

    a = np.array(np.random.random(10000),dtype=np.float64)
    bins = 20
    res = numba_gpu_histogram(a, bins)
    print(res)

