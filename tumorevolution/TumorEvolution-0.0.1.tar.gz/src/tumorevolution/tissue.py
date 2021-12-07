#!/usr/bin/env python3

import numpy as np
import random
import time
import cell

class Tissue ( object ) :

    """ Conceptual class that represents tissue where cells are.

    :param omega: percentage of cancerous cells in the whole population at which the tumor can be detected 
    :type omega: double
    :param alpha: treatment factor between 0 and 1 that decreases at each iteration the fitness of a cancerous cell that receives the treatment
    :type alpha: double
    :param generation_time: number of iterations the treatment is effective on a cancerous cell
    :type generation_time: int
    """
    
    def __init__(self, omega, alpha, generation_time):
        self.generation_time = generation_time
        self.omega = omega
        self.alpha = alpha
        self.cancer_detection = False
        self.current_cure = None
        self.pop = []
        self.clones_pop = {0: {"fitness" : 1,"mu": 0.001, "freq" : 0}}    
    
    def initial_population(self, N = 1000, prop_cancer = 0.01, init_clones=3):
        """Constructor method
        """
        
        nb_cancer_cells = round(prop_cancer *N)
        
        for i in range(1,init_clones+1):
            self.clones_pop[i] = self.clones_pop.get(i, {"fitness" :round(random.uniform(1,3), 3), 
                                                 "mu": round(random.uniform(0, 0.05), 4), 
                                                "freq" : 0})
        
        for i in range(N):
            if (i < nb_cancer_cells) :
                state = "CANCEROUS"
                clone = random.choice(range(1, len(self.clones_pop.keys())))
                
            else :
                state = "NORMAL"
                clone = 0
            
            fitness = self.clones_pop[clone]["fitness"]
            mutation_rate = self.clones_pop[clone]["mu"]  
                
            new_cell = cell.Cell(state, clone, fitness, mutation_rate)
            self.pop.append(new_cell)
            self.clones_pop[clone]["freq"] += 1 
            
    def stats(self):
        """Compute some statistics about the cell population.

        :return: a tuple with statistics for each time step : total number of cells (remains constant btw), number of cancerous cells, number of clone types, and average fitness
        :rtype: tuple 
        """
        nb_cells = len(self.pop)
        nb_normal_cells = self.clones_pop[0]["freq"]
        nb_cancer_cells = nb_cells - nb_normal_cells
        nb_clones = 0
        
        average_fitness = sum([cell.fitness for cell in self.pop])/(nb_cells)
        
        for key in list(self.clones_pop.keys()):
            if (key != 0 and self.clones_pop[key]["freq"] > 0):
                nb_clones +=1
        
        if (nb_cancer_cells >= self.omega * nb_cells):
            self.cancer_detection = True
        else:
            self.cancer_detection = False
 
        return (nb_cells, nb_normal_cells, nb_cancer_cells, nb_clones, average_fitness)
            
    def targeted_treatment(self, n=5):
        
        if (n>len(self.clones_pop)) :
            n = len(self.clones_pop) -1
        
        # if the cancer has been detected and no cure in progress
        if (self.cancer_detection == True and self.current_cure == None):
            
            # find the biggest colonie of mutant clone to treat in prority
            self.current_cure = [clones[0] for clones in sorted({k:self.clones_pop[k] for k in self.clones_pop if k!=0}.items(), 
                                   key=lambda item: item[1]["freq"], 
                                   reverse=True)[:n]]
            
            for cell in self.pop:
                if (cell.clone in self.current_cure):
                    cell.treatment_duration = 0
                    cell.treatment(self.alpha)
                    
        # if there is already a cure on specific clone in progress, just continue it until the end of generation time                
        if(self.current_cure != None):
            remaining_cells_to_treat = 0
            for cell in self.pop:
                if(cell.clone in self.current_cure and cell.treatment_duration < self.generation_time):
                    cell.treatment(self.alpha)
                    remaining_cells_to_treat += 1
            
            if (remaining_cells_to_treat == 0):
                self.current_cure = None
                for cell in self.pop:
                    cell.get_cure == False
                    cell.treatment_duration = 0
                        
    
    def reproduce (self, weighted=True):
    
        if (weighted):
            candidat = random.choices(self.pop, weights=[c.fitness for c in self.pop], k=1)[0]
        else:
            candidat = random.choice(self.pop)

        new_cell = cell.Cell(candidat.state, candidat.clone, candidat.fitness, candidat.mutation_rate)
        
        
        #Proba of mutation : give birth to a new clone type
        proba_mutation = random.uniform(0, 1) 
        if proba_mutation < new_cell.mutation_rate :
            new_clone_id=len(self.clones_pop.keys())
            new_cell.mutate(new_clone_id)
            self.clones_pop[new_cell.clone] = self.clones_pop.get(new_cell.clone, {"fitness" :new_cell.fitness, 
                                         "mu": new_cell.mutation_rate, 
                                        "freq" : 1})
        else:
            self.clones_pop[new_cell.clone]["freq"] += 1
        
        self.pop.append(new_cell)
    
    def get_apoptose(self, weighted = True):
        if (weighted):
            cell = random.choices(self.pop, weights=[1/(c.fitness+0.01) for c in self.pop], k=1)[0]
        else:
            cell = random.choice(self.pop)
            
        self.pop.remove(cell)
        self.clones_pop[cell.clone]["freq"] -= 1 


if __name__ == "__main__" :
	
	print("tissue")
