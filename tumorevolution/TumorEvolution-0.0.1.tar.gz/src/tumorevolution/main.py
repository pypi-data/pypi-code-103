#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import simulation

def make_plot(df1, df2, runs, fig_size=(18,14)):
    fig, axs = plt.subplots(2, 2, figsize=fig_size)

    axs[0, 0].plot(range(runs), df1["Normal cells"].values, label = "normal cells")
    axs[0, 0].plot(range(runs), df1["Tumor cells"].values, label = "cancerous cells")
    axs[0, 0].set_title('Simulation without treatment')
    axs[0, 0].legend()

    axs[0, 1].plot(range(runs), df2["Normal cells"].values, label = "normal cells")
    axs[0, 1].plot(range(runs), df2["Tumor cells"].values, label = "cancerous cells")
    axs[0, 1].set_title('Simulation with treatment')
    axs[0, 1].legend()

    axs[1, 0].plot(range(runs), df1["Number of clones"], label = "number of clones without treatment", color="lightcoral")
    axs[1, 0].plot(range(runs), df2["Number of clones"], label = "number of clones with treatment", color="forestgreen")
    axs[1, 0].set_title('Number of clones')
    axs[1, 0].legend()

    axs[1, 1].plot(range(runs), df1["Average fitness"].values, label = "average fitness without treatment", color="lightcoral")
    axs[1, 1].plot(range(runs), df2["Average fitness"].values, label = "average fitness with treatment", color="forestgreen")
    axs[1, 1].set_title('average fitness')
    axs[1, 1].legend()

    plt.show()

    return(fig, axs)

if __name__ == "__main__" :

    random.seed(time.time())

    N_runs = 10000

    #Without treatment :
    simulation1 = simulation.run(nb_runs=N_runs, 
                      N=2000, 
                      prop_cancer= 0.1, 
                      treatment=False, 
                      verbose=True,
                      weighted_reproduction = True,
                      weighted_apoptosis = True,
                      init_clones=5)


    #With treatment :
    simulation2 = simulation.run(nb_runs=N_runs, 
                       N=2000, 
                       prop_cancer=0.1, 
                       omega=0.2, 
                       alpha=0.5, T=5, 
                       treatment=True, 
                       nb_treatments=3, 
                       verbose=True,
                       weighted_reproduction = True,
                       weighted_apoptosis = True,
                       init_clones=5)


    fig, axs = make_plot(simulation1, simulation2, N_runs)
    fig.savefig("Figure.png", format = "png",  dpi = 500)
