"""A Python implementation of the EMuLSion framework.
(Epidemiologic MUlti-Level SImulatiONs).

Tools for calculating wing transmission's quantity and referential
transformation.

"""
import numpy                    as np
import scipy.special            as sp

from   emulsion.tools.state import StateVarDict

BASE_PARAM = StateVarDict(
    ay=0.34,
    by=0.82,
    az=0.275,
    bz=0.82,

    grav=9.8,    # gravitational acceleration (m/s^2)
    mud=1.8e-5, # dynamic viscosity of air (kg/m.s)
    rhoden=1150,   # kg/m3; # 1.15 grams/cm3 (Godin et al 2007) for E. coli
    # diameter of aerosol generated
    # (Human Respiratory Viral Infections Singh 2014)
    R=1e-6,   # 10 µm 1µm < diameter < 50µm
    W_dep=0.01,
)
BASE_PARAM.W_set = 2 * BASE_PARAM.rhoden * BASE_PARAM.grav *\
                   (BASE_PARAM.R**2) / (9 * BASE_PARAM.mud)


def referential_transform(x, y, theta):
    """Change the referential for rotations."""
    rot = np.array([[np.cos(theta), np.sin(-theta)],
                    [np.sin(theta), np.cos(theta)]])
    return tuple(np.dot(rot, [x, y]))

def plume_ermak(velocity, quantity, x, y, z=4, z_origin=4,
                ay=0.34, az=0.275, by=0.82, bz=0.82,
                grav=9.8, mud=1.8e-5, rhoden=1150, R=1e-6, W_dep=0.01):
    """ERMAK: Compute contaminant concentration (kg/m^3) using the
    Gaussian plume model, modified for a deposition and settling
    velocity.  This code handles a single source (located at the
    origin) and multiple receptors.

    Warning: Python can't handle long double to compute exp()*erfc().
    If we want to increase the precision, we should pass the computation by C.

    """
    if x <= 0 or quantity == 0 or velocity == 0:
        return 0

    W_set = 2 * rhoden * grav * (R**2) / (9*mud)

    sigma_y = ay * (x**by) if x > 0 else 0.
    sigma_z = az * (x**bz) if x > 0 else 0.
    sigma_y2 = sigma_y ** 2
    sigma_z2 = sigma_z ** 2

    W_0 = W_dep - 0.5 * W_set
    Kz = 0.5 * az * bz * velocity * (x**(bz-1))

    C = quantity / (2 * np.pi * velocity * sigma_y * sigma_z)\
        * np.exp(-0.5 * y**2 / sigma_y2)

    C *= np.exp(-(0.5 * W_set * (z - z_origin) / Kz +\
                  W_set**2 * sigma_z2 / 8 / Kz / Kz))

    part = np.exp(-0.5 * (z - z_origin)**2 / sigma_z2) +\
           np.exp(-0.5 * (z + z_origin)**2 / sigma_z2) -\
           (2 * np.pi)**0.5 * W_0 * sigma_z / Kz *\
           np.exp(W_0 * (z + z_origin) / Kz + 0.5 * W_0**2 * sigma_z2 / Kz**2)\
           * sp.erfc(W_0 * sigma_z / 2**0.5 / Kz + (z + z_origin)\
                     / 2**0.5 / sigma_z)

    # Filter values non computable by Python
    part = 0. if np.isnan(part) or np.isinf(part) else part
    return C * part, W_dep

def plume_gaussian(velocity, quantity, x, y, z=4, z_origin=4,
                   ay=0.34, az=0.275, by=0.82, bz=0.82):
    """ERMAK: Compute contaminant concentration (kg/m^3) using the
    Gaussian plume model.

    """
    if x <= 0 or quantity == 0 or velocity == 0:
        return 0
    sigma_y = ay * (x**by) if x > 0 else 0.
    sigma_z = az * (x**bz) if x > 0 else 0.
    sigma_y2 = sigma_y ** 2
    sigma_z2 = sigma_z ** 2

    # Unused expression found in Yu-Lin's code - 2018-02-26
    # apparently a copy-paste vestige from plume_ermak !
    # Kz = 0.5 * az * bz * velocity * (x ** (bz-1))

    C = quantity / (2 * np.pi * velocity * sigma_y * sigma_z)\
        * np.exp(-0.5 * y**2 / sigma_y2)
    part = np.exp(-0.5 * (z - z_origin)**2 / sigma_z2) +\
           np.exp(-0.5 * (z + z_origin)**2/ sigma_z2)

    return C * part
