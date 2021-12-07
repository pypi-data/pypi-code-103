#!/usr/bin/env python3

import numpy as np
import random
import time

class Cell (object) :

    """This is a conceptual class that represent cell individual.

    :param state: Indicate the medical state of the cell; "NORMAL" or "CANCEROUS", defaults to "NORMAL"
    :type state: str
    :param clone: The type of clone the cell belongs to, defaults to 0
    :type clone: int
    :param fitness: Describes the capacity of a cell to successful reproduce itself by natural selection, defaults to 1
    :type fitness: double
    :param mutation_rate: Mutation rate of giving birth of a new type of clone mutant, defaults to 0.001
    :type mutation_rate: double
    """
   
    next_ID = 0
    """Parameter that counts the number of cells and which is used to set the ID for the next created cell.
    """
    
    def __init__(self, state = "NORMAL", clone = 0, fitness = 1, mutation_rate = 0.001):

        """Constructor method
        """
        self.state = state
        self.fitness = fitness
        self.clone = clone
        self.mutation_rate = mutation_rate
        self.ID = Cell.next_ID
        self.get_cure = False
        self.treatment_duration = 0
        Cell.next_ID += 1
        
    def __str__(self):
        """Constructor string method
        """

        return "Cell #{0} of state : {1} and clone type {2}, with a fitness of {3}".format(self.ID, self.state, self.clone, self.fitness)
    
    def mutate (self, new_clone_id):
        """Mutate a selected cell to another type of clone, with new fitness and mutation_rate drawn at random.
        
        :param new_clone_id: New type of clone the mutated cell will belong to
        :type new_clone_id: int, optional 
        """

        if self.state == "NORMAL":
            self.state = "CANCEROUS"
            
        self.clone = new_clone_id
        self.fitness = round(random.uniform(0,2), 3)
        self.mutation_rate = round(random.uniform(0, 0.05), 4)
        
    def treatment (self, alpha):
        self.get_cure == True
        self.fitness = self.fitness * alpha
        self.treatment_duration += 1

if __name__ == "__main__" :
    cell1 = Cell()
    cell2 = Cell(fitness=0.52)
    cell3 = Cell(state="CANCEROUS", clone=1)
    print(cell1)
    print(cell2)
    print(cell3)