import sys
sys.path.append("../../")
from TwoSampleHC_package.TwoSampleHC import two_sample_pvals
from TwoSampleHC_package.TwoSampleHC import HC
import numpy as np

N = 1000 # number of features
n = 5 * N #number of samples

P = 1 / np.arange(1,N+1) # Zipf base distribution
Q = P.copy()
Q[:10] += .1
P = P / P.sum()
Q = Q / Q.sum()

np.random.seed(0)
smp_P = np.random.multinomial(n, P)  # sample form P
smp_Q = np.random.multinomial(n, Q)  # sample from Q

pv = two_sample_pvals(smp_Q, smp_P) # binomial P-values
hc = HC(pv)
hc_star, p_th_star = hc.HCstar(gamma = 0.25) # Higher Criticism test
hcv, p_th = hc.HC(gamma = 0.25) # Higher Criticism test

print("hcv = ", hcv)
print("hc_star = ", hc_star)
print("p_th_star = ", p_th_star)
print("p_th = ", p_th)

assert(np.abs(hcv - 1.93) < .01)
assert(np.abs(hc_star - 1.85) < .01)
assert(np.abs(p_th - 0.00013) < .0001)
assert(np.abs(p_th_star - 0.0014) < .0001)

