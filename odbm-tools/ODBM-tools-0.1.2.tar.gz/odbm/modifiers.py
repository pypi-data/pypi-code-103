from overrides import overrides, final
from odbm.odbm import Mechanism
import numpy as np
import re

class Modifier(Mechanism):
    """
    A superclass class used to handle basic Mechansim modification functionality. Inherits from Mechanism.
    Other mechanism should inherint this class and override attributes and apply(rxn_rate)

    Attributes
    ----------
    name : str
        label used to identify mechanism
    required_params : list
        list with parameter strings, default []
    nS : int
        number of required substrates, default np.nan
    nC : int
        number of required cofactors, default np.nan
    nP : int
        number of required products, default np.nan
    nE : int
        number of required enzymes, default np.nan

    Methods
    -------
    apply(rxn_rate: str):
        Apply modification to reaction rate string

    """

    name = 'base_modifier'  # name for the mechanism
    required_params = []    # list of required parameters

    @overrides
    @final
    def writeEquation(self) -> str:
        return

    def apply(self, rxn_rate: str) -> str:
        """
        Apply modification to reaction rate string

        Parameters
        ----------
        rxn_rate : str
            Original reaction rate

        Returns
        -------
        str
            Modified reaction rate
        """
        return

class LinearCofactor(Modifier):
    name = 'LC'                                     
    required_params = ['maxC']                     
    nC = 1

    @overrides
    def apply(self, rxn_rate) -> str:
        C = self.cofactors[0] # what if there are multiple cofactors?
        maxC = [p+'_'+self.label for p in self.required_params][0]

        return rxn_rate+' * ('+C+'/'+maxC+')'

class HillCofactor(Modifier):
    name = 'HC'
    required_params = ['Ka','n']
    nC = 1

    @overrides
    def apply(self, rxn_rate: str) -> str:
        C = self.cofactors[0]  # what if there are multiple cofactors? 
        Ka,n = [p+'_'+self.label for p in self.required_params]

        return rxn_rate+' * (1/(1+('+Ka+'/'+C+')^'+n+'))'

class Inhibition(Modifier):
    name = 'base_inhibition'

    def alpha(a, I, Ki) -> str:
        return a+' = (1 + '+I+'/'+Ki+')'
    
    def competitive(var: str, a: str): # change just Km
        mod = a+'*'+var
        return var, mod

    def noncompetitive(var: str, a: str): # change just kcat
        mod = '('+var+'/'+a+')'
        return var, mod

    def uncompetitive(vars: list, a: str): # change both kcat and Km
        mods = []
        for v in vars:
            mods.append('('+v+'/'+a+')')
        return vars, mods

    # for mixed inhibition just call competitive and uncompetitive

class ProductInhibition(Inhibition):
    name = 'PI'
    required_params = ['KiP.+'] # regex to accept multiple. how to specifify which product is affecting which substrate?
    nP = np.nan # or error if 1 ...

    @overrides
    def apply(self, rxn_rate: str) -> str:
        P = [p for p in self.params.keys() if re.match(self.required_params[0], p)]
        for p in P:
            id = p[-1]
            a = 'a'+id+'_'+self.label
            Ki = p+'_'+self.label
            I = self.products[int(id)-1]
            
            Km = 'Km' + id # assuming 1st product inhibits 1st substrate !
            Km, aKm = self.competitive(Km, a)

            rxn_rate = rxn_rate.replace(Km, aKm)
            rxn_rate += '; ' + self.alpha(a, I, Ki)

        return rxn_rate