import numpy as np
from tqdm import trange


class DeconvolutionAlgorithm:
    def __init__(self, response_matrix: np.ndarray):
        self.response_matrix = response_matrix

    def deconvolve_measurement(
            self,
            measurement: np.ndarray,
            iterations: int = 1000,
            init: np.ndarray = None
    ) -> [np.ndarray, np.ndarray]:
        raise NotImplementedError

    def bootstrap_deconvolve_measurement(
            self,
            measurement: np.ndarray,
            errors: np.ndarray,
            iterations: int = 1000,
            bootstraps: int = 100,
            init: np.ndarray = None,
            progress: bool = False
    ) -> [np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        decons = np.zeros((bootstraps, self.response_matrix.shape[1]))
        recons = np.zeros((bootstraps, self.response_matrix.shape[0]))

        rng = trange if progress else range

        for i in rng(bootstraps):
            new_measurement = np.random.normal(measurement, errors)
            decons[i, :], recons[i, :] = self.deconvolve_measurement(new_measurement, iterations, init)

        return decons.mean(axis=0), recons.mean(axis=0), decons.std(axis=0), recons.std(axis=0)


class MLEM(DeconvolutionAlgorithm):
    def deconvolve_measurement(
            self,
            measurement: np.ndarray,
            iterations: int = 1000,
            init: np.ndarray = None
    ) -> [np.ndarray, np.ndarray]:
        decon = np.ones(self.response_matrix.shape[1]) if init is None else init
        weight = self.response_matrix.transpose() * measurement
        norm = self.response_matrix.sum(axis=0)
        norm[norm == 0.0] = 1.0
        while iterations > 0:
            ir = np.dot(self.response_matrix, decon)
            ir[ir < 1.e-10] = 1.e-10
            decon = decon * np.dot(weight, 1.0 / ir) / norm
            iterations -= 1

        recon = np.dot(self.response_matrix, decon)

        return decon, recon
