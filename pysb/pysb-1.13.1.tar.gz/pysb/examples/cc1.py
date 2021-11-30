from pysb import *

Model()

Monomer('A', ['s222', 's333'])
Monomer('C', ['s222'])
Monomer('D')
Monomer('ADP', ['s333'])
Monomer('ATP',)

Parameter('A_0', 1)
Parameter('C_0', 10)
Parameter('ADP_0', 100)
Parameter('ATP_0', 10)

Initial(A(s222=None, s333=None), A_0)
Initial(C(s222=None), C_0)
Initial(ADP(s333=None), ADP_0)
Initial(ATP(), ATP_0)

Parameter('kf', 100)
Parameter('kr', 1)
Parameter('kc', 1)

Rule('Bind_three',
     A(s222=None, s333=None) + C(s222=None) + ADP(s333=None)
     <> A(s222=1, s333=2) % C(s222=1) % ADP(s333=2),
     kf, kr)

Rule('catalyze_C_to_D',
     A(s222=1, s333=2) % C(s222=1) % ADP(s333=2)
     >> A(s222=None, s333=None) + D() + ATP(),
     kc)
