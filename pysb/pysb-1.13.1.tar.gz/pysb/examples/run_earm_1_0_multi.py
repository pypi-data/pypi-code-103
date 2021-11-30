#!/usr/bin/env python
"""Reproduce figures 4A and 4B from the EARM 1.0 publication (Albeck et
al. 2008)."""

from pysb.simulator import ScipyOdeSimulator, SimulationResult
import numpy as np

from pysb.examples.earm_1_0 import model


t = np.linspace(0, 6*3600, 6*60+1)  # 6 hours
sim = ScipyOdeSimulator(model, tspan=t)

species = [s for s, p in model.initial_conditions]
x = np.array([p.value for s, p in model.initial_conditions])
new_x = np.clip(x + x * 0.2 * np.random.randn(2, len(x)), 0, None).T
initials = dict(zip(species, new_x))

res = sim.run(initials=initials)
res.custom_attrs = {
    'uint': 18446744073709551615,
    'sint': -9223372036854775808,
    'float': np.pi,
    'complex': 2.3+4.5j,
    'ulong': 18446744073709551616,
    'slong': -9223372036854775809,
    'str': 'Hello str!',
    'bytes': b'Hello \x01\x02\x03 bytes!',
    'unicode': u'Hello \u2603 and \U0001f4a9!',
    'set': {1,2,3,'banana'},
}

res.save('out.h5')
