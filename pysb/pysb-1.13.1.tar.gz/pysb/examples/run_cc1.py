import numpy as np
from pysb.simulator import ScipyOdeSimulator

from cc1 import model


tspan = np.linspace(0, 20, 1000)
sim = ScipyOdeSimulator(model, tspan)
res = sim.run()

# If you don't have pandas or matplotlib then here is a quick printout of the
# species trajectories. Note that the "short name" code here only works for
# simple species (no states, only one way for each monomer to bind).
for s in model.species:
    m_names = [mp.monomer.name for mp in s.monomer_patterns]
    short_name = '+'.join(sorted(m_names, key=len))
    print '   %-9s' % short_name,
print
np.set_printoptions(precision=7, suppress=True)
print(res.all[::40])

# With pandas and matplotlib we can easily plot the trajectories instead.
import matplotlib.pyplot as plt
res.dataframe.plot()
plt.gca().set_yscale('log')
plt.legend(model.species)
plt.show()
