import h5py
import matplotlib.pyplot as plt
import numpy as np

from pyechelle.spectrograph import ZEMAX, trace, traceNative


def plot_transformations(spectrograph: ZEMAX):
    """

    Args:
        spectrograph: Spectrograph model

    Returns:

    """
    fig, ax = plt.subplots(2, 3, 'all')
    fig.suptitle(f"Affine transformations of {spectrograph.name}")
    for o in spectrograph.order_keys:
        ax[0, 0].set_title("sx")
        ax[0, 0].plot(spectrograph.transformations[o].sx)
        ax[0, 1].set_title("sy")
        ax[0, 1].plot(spectrograph.transformations[o].sy)
        ax[0, 2].set_title("shear")
        ax[0, 2].plot(spectrograph.transformations[o].shear)
        ax[1, 0].set_title("rot")
        ax[1, 0].plot(spectrograph.transformations[o].rot)
        ax[1, 1].set_title("tx")
        ax[1, 1].plot(spectrograph.transformations[o].tx)
        ax[1, 2].set_title("ty")
        ax[1, 2].plot(spectrograph.transformations[o].ty)
    plt.show()


def plot_transformation_matrices(spectrograph: ZEMAX):
    """

    Args:
        spectrograph: Spectrograph model

    Returns:

    """
    fig, ax = plt.subplots(2, 3, 'all')
    fig.suptitle(f"Affine transformation matrices of {spectrograph.name}")
    for o in spectrograph.order_keys:
        ax[0, 0].set_title("m0")
        ax[0, 0].plot(spectrograph.transformations[o].m0)
        ax[0, 1].set_title("m1")
        ax[0, 1].plot(spectrograph.transformations[o].m1)
        ax[0, 2].set_title("m2")
        ax[0, 2].plot(spectrograph.transformations[o].m2)
        ax[1, 0].set_title("m3")
        ax[1, 0].plot(spectrograph.transformations[o].m3)
        ax[1, 1].set_title("m4")
        ax[1, 1].plot(spectrograph.transformations[o].m4)
        ax[1, 2].set_title("m5")
        ax[1, 2].plot(spectrograph.transformations[o].m5)
    plt.show()


def plot_psfs(spectrograph: ZEMAX):
    """
    Plot PSFs as one big map
    Args:
        spectrograph: Spectrograph model

    Returns:

    """
    plt.figure()
    n_orders = len(spectrograph.order_keys)
    n_psfs = max([len(spectrograph.psfs[k].psfs) for k in spectrograph.psfs.keys()])
    shape_psfs = spectrograph.psfs[next(spectrograph.psfs.keys().__iter__())].psfs[0].data.shape
    img = np.empty((n_psfs * shape_psfs[0], n_orders * shape_psfs[1]))
    for oo, o in enumerate(spectrograph.order_keys):
        for i, p in enumerate(spectrograph.psfs[f"psf_{o[:5]}" + "_" + f"{o[5:]}"].psfs):
            if p.data.shape == shape_psfs:
                img[int(i * shape_psfs[0]):int((i + 1) * shape_psfs[0]),
                int(oo * shape_psfs[1]):int((oo + 1) * shape_psfs[1])] = p.data
    plt.imshow(img, vmin=0, vmax=np.mean(img) * 10.0)
    plt.show()


def plot_fields(spec: ZEMAX):
    plt.figure()
    with h5py.File(spec.modelpath, 'r') as h5f:
        for k in h5f.keys():
            if 'fiber_' in k:
                a = h5f[k].attrs['norm_field'].decode('utf-8').split('\n')

                for b in a:
                    if 'aF' in b:
                        print(b[2:])


if __name__ == "__main__":
    import h5py
    from scipy.interpolate import CubicSpline

    cfg_file = h5py.File("cfg.hdf", "w")
    cfg_file["valid"] = np.ones((10560, 10560), dtype=np.int)

    FIBER = []
    ORDER = []
    POSITION = []

    for f in [1, 2]:
        spectrograph = ZEMAX("../models/lars3.hdf", f)
        for o, ok in zip(spectrograph.orders, spectrograph.order_keys):
            wlrange = spectrograph.get_wavelength_range(o)
            wl = np.linspace(*wlrange, 1000)
            x = y = np.ones_like(wl)*0.5
            sx, sy, rot, shear, tx, ty = spectrograph.transformations[ok].get_transformations_spline(wl)
            xt, yt = traceNative(x, y, sx, sy, rot, shear, tx, ty)
            spl_x = CubicSpline(xt, wl)
            wl_pixel = spl_x(np.arange(10560)+0.5)
            cfg_file[f"wavelengths/fiber_{f}/{ok}"] = wl_pixel

            spl_y = CubicSpline(xt, yt)

            FIBER.append(f)
            ORDER.append(o)
            POSITION.append(spl_y(10560./2.+0.5))

    positions = np.array(np.vstack((FIBER, ORDER, POSITION)), dtype=np.int)
    cfg_file.create_group("identify_stripes")
    cfg_file['identify_stripes'].attrs['positions'] = positions.T
    # print(positions)
