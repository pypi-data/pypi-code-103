# -*- coding: utf-8 -*-
"""
Testing the loglikelihood class
"""

import numpy as np
from scipy import stats

from tripy.kernels import Exponential
from tripy.base import MeasurementSpaceTimePoints

# ============================================================================
# Testing
# ============================================================================
Nx = 5
Nt = 5
lcorr_x = 1.0
lcorr_t = 1.0

# Initialize MeasurementSpaceTimePoints
MS = MeasurementSpaceTimePoints()

# Create space and time coordinates
coords_x = np.sort( np.linspace(0, 1, Nx) + 0.1 * np.random.rand(Nx) )
coords_t = np.sort( np.linspace(0, 1, Nt) + 0.1 * np.random.rand(Nt) )

# Modeling uncertainty
std_model = np.random.rand(Nx) + 0.1
std_meas = np.random.rand(Nx) + 0.1

# Add points and correlation to problem definition
MS.add_measurement_space_points(coords_x, std_model, group="group_1")
MS.add_measurement_space_within_group_correlation("group_1", Exponential)

# Dummy model function
def func_model(theta):
    return np.cos(theta * coords_x)

# Get covariance and inverse covariance matrices
cov_mx = MS.compile_covariance_matrix()
inv_cov_mx = np.linalg.inv(cov_mx)

# Generate measurements
v_obs = np.random.rand(Nx)

def func_loglike_ref(theta, x, y_meas, y_func, std_model, std_meas):

    # Evaluate model and calculate residual
    y_phys = y_func(theta)
    y_res = y_phys - y_meas

    # Assemble covariance
    e_cov_mx = np.diag(std_meas ** 2)
    kernel = Exponential(np.reshape(x, (-1, 1)))
    corr_mx = kernel.eval(std_model, length_scale=lcorr_x)
    kph_cov_mx = np.matmul(
        np.diag(y_phys), np.matmul(corr_mx, np.diag(y_phys))
    )
    cov_mx = kph_cov_mx + e_cov_mx

    # Evaluate the loglikelihoods
    loglike = stats.multivariate_normal.logpdf(y_res, cov=cov_mx)
    return loglike

loglike = Log

# Compare the loglikelihoods
theta = 2.0

loglike_ref = func_loglike_ref(
    theta, coords_x, v_obs, func_model, std_model, std_meas
)
