import sys
sys.path.append("../../")
from TwoSampleHC_package.TwoSampleHC import two_sample_pvals
from TwoSampleHC_package.TwoSampleHC import HC
import numpy as np
from tqdm import tqdm
from scipy.stats import norm

"""
Here we create two multivariate normals with rare
and weak differences in their means. 
"""

GAMMA = .3

def test_sparse_normals(r, n, be, sig):
    mu = 2 * r * np.log(n)
    ep = n ** -be
    idcs1 = np.random.rand(n) < ep / 2
    idcs2 = np.random.rand(n) < ep / 2

    Z1 = np.random.randn(n)
    Z2 = np.random.randn(n)

    Z1[idcs1] = sig*Z1[idcs1] + mu
    Z2[idcs2] = sig*Z2[idcs2] + mu

    Z = (Z1 - Z2)/np.sqrt(2)
    pvals = 2*norm.cdf(- np.abs(Z))

    _hc = HC(pvals)

    return {'hc' : _hc.HC(GAMMA)[0],
            'hcstar' : _hc.HCstar(GAMMA)[0],
            'bj' : _hc.berk_jones(GAMMA)
            }
    




r = 0
n = 1000
be = .75
sig = 1

nMonte = 10000


lo_bj = []
lo_hc = []
lo_hcstar = []
print(f"Testing with parameters: r={r}, n={n}, be={be}, sig={sig}")
for itr in tqdm(range(nMonte)):
    res = test_sparse_normals(r, n, be, sig)
    lo_bj += [res['bj']]
    lo_hc += [res['hc']]
    lo_hcstar += [res['hcstar']]
    
print("Avg(HC) = ", np.mean(lo_hc))
print("Avg(HCstar) = ", np.mean(lo_hcstar))
print("Avg(BerkJones) = ", np.mean(lo_bj))

assert(np.abs(np.mean(lo_hc) - 1.33) < .15)
assert(np.abs(np.mean(lo_hcstar) - 1.29) < .15)
assert(np.abs(np.mean(lo_bj) - 3.9) < .15)


lo_bj = []
lo_hc = []
lo_hcstar = []
r = .75
print(f"Testing with parameters: r={r}, n={n}, be={be}, sig={sig}")
for itr in tqdm(range(nMonte)):
    res = test_sparse_normals(r, n, be, sig)
    lo_bj += [res['bj']]
    lo_hc += [res['hc']]
    lo_hcstar += [res['hcstar']]
    
print("Avg(HC) = ", np.mean(lo_hc))
print("Avg(HCstar) = ", np.mean(lo_hcstar))
print("Avg(BerkJones) = ", np.mean(lo_bj))

assert(np.abs(np.mean(lo_hc) - 2.52) < .15)
assert(np.abs(np.mean(lo_hcstar) - 2.3) < .15)
assert(np.abs(np.mean(lo_bj) - 94.5) < 1)
