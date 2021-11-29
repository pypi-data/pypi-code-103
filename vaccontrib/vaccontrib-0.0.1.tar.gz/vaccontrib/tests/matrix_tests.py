import unittest

import numpy as np

from vaccontrib.covid import get_next_generation_matrix_covid
from vaccontrib.linalg import get_spectral_radius_and_eigenvector, convert_4d_matrix_to_2d_block
from vaccontrib.main import (
                get_next_generation_matrix_from_matrices,
                get_reduced_contribution_matrix,
                get_contribution_matrix,
                get_reduced_vaccinated_susceptible_contribution_matrix,
                get_homogeneous_contribution_matrix,
            )
import vaccontrib.io as io

class NextGenMatrixTest(unittest.TestCase):

    def test_next_generation_matrix(self):
        """
        """

        R0 = np.array([1.,4.,4.,4.,4.])
        variant = 'alpha'
        gamma = io.get_contact_matrix()
        S = io.get_disease_free_state()
        N = io.get_population_sizes()
        s = io.get_susceptibility_reduction(variant=variant)
        r = io.get_transmissibility_reduction(variant=variant)
        a = io.get_relative_infection_rate(variant=variant)
        b = io.get_relative_recovery_rate(variant=variant)

        M, _ = gamma.shape
        _, V = S.shape

        a0 = a[:,0]
        b0 = b[:,0]

        K0 = gamma.dot(np.diag(a0)).dot(np.diag(1/b0))
        rho0, _ = get_spectral_radius_and_eigenvector(K0)

        if not hasattr(R0,'__len__'):
            R0 = np.ones(V) * R0

        K = np.zeros((M,M,V,V))
        for i in range(M):
            for j in range(M):
                for G in range(V):
                    for L in range(V):
                        K[i,j,G,L] = R0[L] / rho0 * gamma[i,j] * (1-s[i,G]) * (1-r[j,L]) *\
                                     S[i,G] * a[j,L] / b[j,L] / N[j]

        _K = get_next_generation_matrix_covid(R0,variant=variant)

        assert(np.all(np.isclose(K,_K)))

    def test_4d_matrix_as_2d_block(self):
        gamma = np.array([[1.,1.],[1.,1.]])
        S = np.array([[0.4,0.6],[0.4,0.6]])
        N = np.array([1.,1.])
        s = np.array([[0.,1],[0.,1]])
        r = np.array([[0.,0.],[0.,0.]])
        a = np.array([[1.,1.],[1.,1.]])
        b = np.array([[1.,1.],[1.,1.]])

        R0 = 4

        K = get_next_generation_matrix_from_matrices(R0,gamma,S,N,s,r,a,b)
        K1 = convert_4d_matrix_to_2d_block(K)

        M, _, V, __ = K.shape
        rows = []
        for row in np.array_split(K,M,axis=0):
            rows.append([])
            for col in np.array_split(row,M,axis=1):
                rows[-1].append(col.reshape(V,V))

        K2 = np.block(rows)

        assert(np.all(np.isclose(K1,K2)))


    def test_spectrum(self):
        gamma = np.array([[1.,1.],[1.,1.]])
        S = np.array([[0.4,0.6],[0.4,0.6]])
        N = np.array([1.,1.])
        s = np.array([[0.,0.],[0.,0.]])
        r = np.array([[0.,0.],[0.,0.]])
        a = np.array([[1.,1.],[1.,1.]])
        b = np.array([[1.,1.],[1.,1.]])

        R0 = 4

        K = get_next_generation_matrix_from_matrices(R0,gamma,S,N,s,r,a,b)

        K = convert_4d_matrix_to_2d_block(K)
        R, y = get_spectral_radius_and_eigenvector(K)

        assert(np.isclose(R0,R))

    def test_spectrum(self):
        gamma = np.array([[1.,1.],[1.,1.]])
        S = np.array([[0.4,0.6],[0.4,0.6]])
        N = np.array([1.,1.])
        s = np.array([[0.,0.],[0.,0.]])
        r = np.array([[0.,0.],[0.,0.]])
        a = np.array([[1.,1.],[1.,1.]])
        b = np.array([[1.,1.],[1.,1.]])

        R0 = 4

        K = get_next_generation_matrix_from_matrices(R0,gamma,S,N,s,r,a,b)

        K = convert_4d_matrix_to_2d_block(K)
        R, y = get_spectral_radius_and_eigenvector(K)

        assert(np.isclose(R0,R))

    def test_reduced(self):
        gamma = np.array([[1.,1.],[1.,1.]])
        S = np.array([[0.4,0.3,0.3,],[0.4,0.3,0.3]])
        N = np.array([1.,1.])
        s = np.array([[0.,0.,0.],[0.,0.,0.]])
        r = np.array([[0.,0.,0.],[0.,0.,0.]])
        a = np.array([[1.,1.,1.],[1.,1.,1.]])
        b = np.array([[1.,1.,1.],[1.,1.,1.]])

        R0 = 4
        K1 = get_next_generation_matrix_from_matrices(R0,gamma,S,N,s,r,a,b)
        C1 = get_reduced_vaccinated_susceptible_contribution_matrix(K1)

        S = np.array([[0.4,0.6,],[0.4,0.6]])
        K2 = get_next_generation_matrix_from_matrices(R0,gamma,S,N,s[:,:2],r[:,:2],a[:,:2],b[:,:2])
        C2 = get_reduced_vaccinated_susceptible_contribution_matrix(K2)

        assert(np.all(np.isclose(C2, C1)))

    def test_homogeneous(self):

        _v = 0.69
        _s = 0.85
        _r = 0.5
        R0 = [2.234,4.]

        gamma = np.array([[1.]])
        S = np.array([[1-_v,_v]])
        N = np.array([1.])
        s = np.array([[0.,_s]])
        r = np.array([[0.,_r]])
        a = np.array([[1.,1.]])
        b = np.array([[1.,1.]])

        K1 = get_next_generation_matrix_from_matrices(R0,gamma,S,N,s,r,a,b)
        C1 = get_reduced_vaccinated_susceptible_contribution_matrix(K1)

        C2 = get_homogeneous_contribution_matrix(R0, _v, _s, _r)

        assert(np.all(np.isclose(C1,C2)))




if __name__ == "__main__":

    T = NextGenMatrixTest()
    T.test_next_generation_matrix()
    T.test_4d_matrix_as_2d_block()
    T.test_spectrum()
    T.test_reduced()
    T.test_homogeneous()
