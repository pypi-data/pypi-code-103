#!/usr/bin/env python3

import numpy as np
import pandas as pd
import random
import time
import cell
import tissue

def run (nb_runs=10000, 
         N=1000, 
         prop_cancer=0.1, 
         omega=0.2, 
         alpha=0.5, 
         T=20, 
         treatment = True, 
         nb_treatments = 5, 
         verbose = True,
         weighted_reproduction = True,
         weighted_apoptosis = True, 
         init_clones = 3):


    """Fetch all the parameters given by the user and performs a simulation according to the type of model the user wants.
    
    :param nb_runs: Number of iterations of the simulation 
    :type nb_runs: int
    :param N: Number of cells within the tissue
    :type N: int
    :param prop_cancer: initial percentage of cancerous cell in the population
    :type prop_cancer: double
    :param omega: percentage of cancerous cells in the whole population at which the tumor can be detected 
    :type omega: double
    :param alpha: treatment factor between 0 and 1 that decreases at each iteration the fitness of a cancerous cell that receives the treatment
    :type alpha: double
    :param T: max number of generation_time (refer to the :class: `tissue.Tissue`) for a cell receiving the treatment
    :type T: int
    :param treatment: if the user wants to apply a treatment during the simulation
    :type treatment: boolean
    :param nb_treatment: as a treatment is specific to a clone type, we can apply consecutive treatment, i.e., cure multiple clone types at once.
    :type nb_treatment: int
    :param verbose: print the status of the simulation
    :type verbose: boolean
    :param weighted_reproduction: use the cell fitness to weight the cell division process
    :type weighted_reproduction: boolean
    :param weighted_apoptosis: use the cell fitness to weight the cell apoptosis process
    :type weighted_apoptosis: boolean
    :param init_clones: number of initial clone type we put at the beginning of the simulation
    :type init_clones: int
    """
    
    my_tissue = tissue.Tissue(omega, alpha, T)
    my_tissue.initial_population(N, prop_cancer, init_clones=init_clones)
    
    if verbose:
        print("Initilisation : ")
        print ( "Total number of cells : {}, number of normal cells : {}, number of cancerous cells {}".format(my_tissue.stats()[0], my_tissue.stats()[1], my_tissue.stats()[2]) ) 
        print ( "\n" )
        
    nb_cells = []
    nb_normal_cells = []
    nb_cancer_cells = []
    nb_clones = []
    averages_fitness = []
    
    for i in range (nb_runs):
        random.seed(time.time())
        my_tissue.reproduce(weighted_reproduction)
        my_tissue.get_apoptose(weighted_apoptosis)
        
        if (treatment) :
            my_tissue.targeted_treatment(n=nb_treatments)
        
        nb_cells.append(my_tissue.stats()[0])
        nb_normal_cells.append(my_tissue.stats()[1])
        nb_cancer_cells.append(my_tissue.stats()[2])
        nb_clones.append(my_tissue.stats()[3])        
        averages_fitness.append(my_tissue.stats()[4])
    
    df = pd.DataFrame({"Total cells" : nb_cells, 
                  "Normal cells" : nb_normal_cells, 
                  "Tumor cells" : nb_cancer_cells, 
                  "Number of clones": nb_clones, 
                  "Average fitness" : averages_fitness, 
                  })
        
    if verbose :
        print ( "Statistics after", nb_runs, "runs : ")
        print ( "Total number of cells : {}, number of normal cells : {}, number of cancerous cells : {}".format(nb_cells[-1], nb_normal_cells[-1], nb_cancer_cells[-1], "\n" ) )
        print ( "\n" )
        
    return (df)

if __name__ == "__main__" :
	print("simulation")
