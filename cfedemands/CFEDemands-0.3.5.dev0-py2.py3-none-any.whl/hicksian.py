# [[file:../Demands/demands.org::hicksian][hicksian]]
# Tangled on Mon Aug 30 14:39:30 2021
from . import frischian
from ._utils import check_args
from ._core import lambdaforU
from numpy import array

def expenditurefunction(U,p,parms,NegativeDemands=True):

    n,parms = check_args(p=p,**parms)

    x=demands(U,p,parms,NegativeDemands=NegativeDemands)

    return sum(array([p[i]*x[i] for i in range(n)]))

def demands(U,p,parms,NegativeDemands=True):

    n,parms = check_args(p=p,**parms)
    lbda=lambdaforU(U,p,parms,NegativeDemands=NegativeDemands)

    return frischian.demands(lbda,p,parms,NegativeDemands=NegativeDemands)

def budgetshares(U,p,parms,NegativeDemands=True):

    n,parms = check_args(p=p,**parms)
    
    h=demands(U,p,parms,NegativeDemands=NegativeDemands)
    y=expenditurefunction(U,p,parms,NegativeDemands=NegativeDemands)

    return array([p[i]*h[i]/y for i in range(n)])
# hicksian ends here
