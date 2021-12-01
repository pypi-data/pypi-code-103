# SPDX-FileCopyrightText: 2020 G2Elab / MAGE
#
# SPDX-License-Identifier: Apache-2.0

__author__ = "B.Delinchant / G2ELab"

# Using AUTOGRAD : Don't use
#     Assignment to arrays A[0,0] = x
#     Implicit casting of lists to arrays A = np.sum([x, y]),
#     use A = np.sum(np.array([x, y])) instead.
#     A.dot(B) notation (use np.dot(A, B) instead)
#     In-place operations (such as a += b, use a = a + b instead)
#     Some isinstance checks, like isinstance(x, np.ndarray) or
#     isinstance(x, tuple), without first doing from autograd.builtins
#     import isinstance, tuple.

#https://en.wikipedia.org/wiki/Test_functions_for_optimization

import autograd.numpy as np
def simionescu(x, y, rr, rs, n):
    fobj = 0.1 * x * y
    ctr = x * x + y * y - np.power(rr + rs * np.cos(n * np.arctan(x / y)), 2)
    return locals().items()

from noload.tutorial.plotTools import plot3D
#plot3D(simionescu, [[-1.25,1.25],[-1.25,1.25]], outNames = ['fobj','ctr'],
# parameters = (1,0.2,8))


#Optimize
from noload.optimization.optimProblem import Spec, OptimProblem
#This function is non defined in [0,0], initial guess must be different
# from [0,0]
spec = Spec(variables={'x':0, 'y':1}, bounds={'x':[-1.25, 1.25],
                            'y':[-1.25, 1.25]}, objectives=['fobj'],
            ineq_cstr={'ctr':[None, 0]} #inequality constraints
            )
#spec = Spec(variables=['x', 'y'], bounds=[[-1.25, 1.25], [-1.25, 1.25]],
# objectives=['fobj'], xinit = [0,1], ineq_cstr=['ctr'],
# ineq_cstr_bnd=[[None, 0]], #inequality constraints ) # DEPRECIATED METHOD
optim = OptimProblem(model=simionescu, specifications=spec,
                     parameters={'rr':1, 'rs':0.2, 'n':8})
result = optim.run()

result.printResults()
result.plotResults()

#It is also possible to iterate by yourself to get results
for name, value in result.getLastInputs().items():
    print(name, '  \t =', value)
for name, value in result.getLastOutputs().items():
    print(name, '  \t =', value)
