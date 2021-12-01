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

def BinhAndKorn(x, y):
    f1 = 4*x**2+4*y**2
    f2 = (x-5)**2+(y-5)**2
    g1 = (x-5)**2+y
    g2 = (x-8)**2+(y+3)**2
    return locals().items()

#f1 : 0 -> 136
#f2 : 4 -> 50

from noload.tutorial.plotTools import plot3D
#plot3D(BinhAndKorn, [[0, 5], [0, 3]], outNames = ['f1','f2','g1','g2'])


#Optimize
from noload.optimization.optimProblem import Spec, OptimProblem
spec = Spec(variables={'x':0, 'y':0}, bounds={'x':[0, 5], 'y':[0, 3]},
            objectives=['f1','f2'],
            ineq_cstr={'g1':[None, 25],'g2':[20, None]} #inequality constraints
            )
#spec = Spec(variables=['x', 'y'], bounds=[[0, 5], [0, 3]],
# objectives=['f1','f2'], xinit = [0,0],
#            ineq_cstr=['g1','g2'], ineq_cstr_bnd=[[None, 25],[20, None]],
#            #inequality constraints ) # DEPRECIATED METHOD
optim = OptimProblem(model=BinhAndKorn, specifications=spec)
result = optim.run()

import noload.gui.plotPareto as pp
#TODO intégrer ça dans le wrapper
#TODO ajouter les contraintes sur le pareto
pp.plot([result.resultsHandler], ['f1', 'f2'], ['Pareto'])
#affichage statique (1 sur 2)

#get constraints for each optimal solutions :
import numpy
g1i = numpy.where(result.resultsHandler.oNames == 'g1')[0][0]
g2i = numpy.where(result.resultsHandler.oNames == 'g2')[0][0]
sols = result.resultsHandler.solutions
for sol in sols:
    print('----------')
    print('x  =', sol.iData[0], '  \ty =', sol.iData[1])
    print('g1 =', sol.oData[g1i], '  \tg2 =', sol.oData[g2i])

#TODO dans result.resultsHandler.print() retouner des une dataframe
# exploitable plus simplement
#result.resultsHandler.print()
#SOLUTIONS of PARETO FRONT
# x	y	f1	f2	ctr1	ctr2
# 0	0	0	50	25	73
# 1.00838475	1.0088955	8.138839733	31.86190744	16.94188783	64.95392698
# 2.38047612	2.38047616	45.33333336	13.72381047	9.242381508	60.52857236
# 3.6968455	3	90.66666668	5.698211644	4.698211644	54.51713863
# 5	3	136	4	3	45

