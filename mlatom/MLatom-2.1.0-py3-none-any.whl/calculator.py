#!/usr/bin/env python3
'''
  !---------------------------------------------------------------------------! 
  ! calculator: module for ASE calculations                                   ! 
  ! Implementations by: Peikung Zheng                                         ! 
  !---------------------------------------------------------------------------! 
'''
import numpy as np
import re
import ase
from ase import io
from ase.calculators.calculator import Calculator, all_changes 
import MLtasks

class MLatomCalculator(Calculator):
    implemented_properties = ['energy', 'forces']
    def __init__(self, optmol=None):
        super(MLatomCalculator, self).__init__()
        self.optmol = optmol

    def calculate(self, atoms=None, properties=['energy'], system_changes=all_changes):
        super(MLatomCalculator, self).calculate(atoms, properties, system_changes)
        
        #print(' \t', end=' ')
        element = self.atoms.get_chemical_symbols()
        coord = self.atoms.get_positions()
        io.write('xyz_temp.dat', self.atoms, format='extxyz', plain=True)

        args2pass = np.loadtxt('taskargs', dtype=str)
        if re.search('aiqm1', ''.join(args2pass), flags=re.IGNORECASE):
            import AIQM1
            AIQM1.AIQM1Cls(args2pass).forward(self.optmol)
        else:   
            args2pass = np.append(args2pass, 'geomopt')
            MLtasks.MLtasksCls.useMLmodel(args2pass)

        energy = np.loadtxt('enest.dat')
        forces = -np.loadtxt('gradest.dat', skiprows=2)
        energy *= ase.units.Hartree
        forces *= ase.units.Hartree

        self.results['energy'] = energy

        if 'forces' in properties:
            self.results['forces'] = forces

