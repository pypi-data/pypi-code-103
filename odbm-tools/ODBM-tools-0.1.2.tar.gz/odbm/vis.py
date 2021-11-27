
import pandas as pd
import numpy as np
import tellurium as te
from odbm.odbm import ModelBuilder
import matplotlib.pyplot as plt

'''
Plot function

Input:
model (ModelBuilder): model class
sim: simulation result, as NamedArray
rxn_idx: list of indices (ints) corresponding to reactions in model definition to plot
'''

def rxn_plot(model:ModelBuilder, sim, rxn_idx = [], figsize = None, titles = None):
    if figsize is None:
        figsize = (len(rxn_idx),3)

    f,ax = plt.subplots(1, len(rxn_idx), figsize = figsize, sharey=False)
    for k,r in enumerate(rxn_idx):
        for j in model.get_substrates(id = r):
            if '['+j+']'.upper() in sim.colnames:
                #if species is not in simulation output, it is a boundary species
                ax[k].plot(sim['time']/60,sim['['+j+']'], label = j)
            else:
                #assumes boundary species are defined with a "$", plots horizontal line
                boundary_species = float(model.species[model.species['Label'] == '$'+j]['StartingConc'])
                ax[k].plot([0,(sim['time']/60)[-1]], [boundary_species, boundary_species], label = j)

        for j in model.get_products(r):
            if '['+j+']'.upper() in sim.colnames:
                #if species is not in simulation output, it is a boundary species
                ax[k].plot(sim['time']/60,sim['['+j+']'],'--', label = j)
            else:
                #assumes boundary species are defined with a "$", plots horizontal line
                boundary_species = float(model.species[model.species['Label'] == '$'+j]['StartingConc'])
                ax[k].plot([0,(sim['time']/60)[-1]], [boundary_species,boundary_species], '--', label = j)


        ax[k].legend()
        if titles: ax[k].set_title(titles[k])

        ax[k].set_xlabel('time (min)')
        ax[k].set_ylabel('Concentraion (mM)')
    f.tight_layout()
    return f, ax