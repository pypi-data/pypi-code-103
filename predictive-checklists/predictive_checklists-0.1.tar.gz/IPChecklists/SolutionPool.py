import numpy as np
import pandas as pd
from pathlib import Path
import pickle
import json
from tqdm import tqdm

class SolutionPool():
    def __init__(self, dataset_name, binarization):
        self.dataset_name = dataset_name
        self.binarization = binarization
        self.pool = []
        self.df = pd.DataFrame(columns = ['ind', 'M', 'N', 'origin'])

    def __len__(self):
        return len(self.pool)

    def add_from_dir(self, dir, origin = None, enforce_fold = None):
        '''
        Adds a directory of trained checklist to the pool, with a given origin (str)
        '''
        for i in Path(dir).glob('**/checklists'):
            args = json.load((i.parent/'args.json').open('r'))
            if enforce_fold is not None and args['fold'] != enforce_fold:
                continue
            if args['dataset'] == self.dataset_name and args['binarization'] == self.binarization:
                checklists = pickle.load(i.open('rb'))
                for checklist in checklists:
                    self.add_to_pool(checklist, origin if origin is not None else args['experiment_name'])

        for i in Path(dir).glob('**/checklist'):
            args = json.load((i.parent/'args.json').open('r'))
            if enforce_fold is not None and args['fold'] != enforce_fold:
                continue
            if args['dataset'] == self.dataset_name and args['binarization'] == self.binarization:
                checklist = pickle.load(i.open('rb'))
                self.add_to_pool(checklist, origin if origin is not None else args['experiment_name'])

    def add_to_pool(self, checklist, origin = None):
        '''
        Adds a single checklist to the pool, with potentially a specified origin (str)
        '''        
        row = {
            'ind': len(self.pool),
            'M': checklist.M,
            'N': checklist.N,
            'origin': origin
        }
        self.pool.append(checklist)
        self.df = self.df.append(row, ignore_index = True)

    def get_subset(self, N = None, N_op = '<=', M = None, M_op = '<=', origin = None):
        '''
        Given a set of constraints, returns a list of Checklist objects that satisfies these constraints
        '''
        self.subset = self.df.copy().query("M >= 1.0")
        if N is not None:
            self.subset = self.subset.query(f"N {N_op} {N}")
        if M is not None:
            self.subset = self.subset.query(f"M {N_op} {M}")
        if origin is not None:
            self.subset = self.subset[self.subset.origin == origin]
        inds = self.subset.ind.values.tolist()
        return [self.pool[c] for c in inds]
        
