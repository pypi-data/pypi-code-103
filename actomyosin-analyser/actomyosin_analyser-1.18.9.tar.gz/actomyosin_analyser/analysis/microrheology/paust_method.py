from typing import Union, Tuple
import numpy as np
from scipy.optimize import curve_fit


def compute_G_via_fit_parameters(
        omega: np.ndarray,
        bead_radius: float,
        kT: float,
        A, B, C, D
) -> np.ndarray:
    """
    With parameters `A, B, C, D` retrieved via function `paust_method.fit_msd`,
    compute the predictions of complex modulus G with the Paust model.
    `omega` is `1/lag_time`.
    Make sure you provide all values in a consistent unit system (i.e. all in
    SI units, or all in some consistent internal units).

    :return: G(omega)
    """
    term1 = -kT * omega**2 * (1 + 1j * D * omega)
    term2 = np.pi * bead_radius * 1j * omega
    term3 = B + 1j * B * D * omega + 1j * omega * (A + C + 1j * A * D * omega)
    return term1 / term2 / term3


def fit_msd(
        lag_time: np.ndarray,
        msd: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply `curve_fit` (from `scipy.optimize`) on the Paust model for given data.

    :return: (0) The optimized parameters, and
             (1) the error covariance matrix (see documentation on `curve_fit`).
    """
    popt, err = curve_fit(paust_model, lag_time, msd,
                          sigma=lag_time,
                          maxfev=10000,
                          ftol=1e-15)
    return np.array(popt), np.array(err)


def paust_model(t: Union[float, np.ndarray],
                A: float, B: float, C: float, D: float) -> Union[float, np.ndarray]:
    """
    This function is the model for the MSD of a microrheolgy probe bead. When you use
    the function `paust_method.fit_msd`, your MSD data gets fitted to this function,
    yielding optimized values for parameters `[A, B, C, D]`.
    Optimized parameters can then be used to predict G with
    function `paust_method.compute_G_via_fit_parameters`.
    """
    return A + B * t + C * (1 - np.exp(-t / D))
