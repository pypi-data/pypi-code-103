#!/usr/bin/env python

import pynmrstar
import numpy as np
import sys
import os

from ansurr import rci_nef_dicts
from ansurr.functions import check_quiet_print


class cs_set(object):
    _registry = []
    def __init__(self,i):
        self._registry.append(self)
        self.i = i
        self.chains = []
        
class chain(object):
    _registry = []
    def __init__(self,i):
        self._registry.append(self)
        self.i = i
        self.residues = []

class res(object):
    _registry = []
    def __init__(self,i,name):
        self._registry.append(self)
        self.i = i
        self.name = name
        self.shifts = [] 
        self.secondary_shifts = []
        self.secondary_shifts_smoothed = []
        self.neighbours = ['',''] 
        self.assumed_RC = 0
        self.shift_types = ''
        self.RCI = 0
        self.RCI_smoothed = 0
        
class atom(object):
    _registry = []
    def __init__(self,atom_type,shift):
        self.atom_type = atom_type
        self.shift = shift
          
def append_shift(res, atom_type, shift):
    try:
        shift = float(shift)
        res.shifts.append(atom(atom_type,shift))
    except:
        pass

def calc_RCI(path_to_nef_file,output_dir='',quiet=False):

    entry = pynmrstar.Entry.from_file(path_to_nef_file)  # read NEF format
    
    cs_result_sets=[]
    for chemical_shift_loop in entry.get_loops_by_category("_nef_chemical_shift"): # get sets of chemical shift files
        cs_result_sets.append(chemical_shift_loop.get_tag(['chain_code', 'sequence_code', 'residue_name', 'atom_name', 'value', 'value_uncertainty']))
        
    if len(cs_result_sets) == 0:
        check_quiet_print(quiet,'no chemical shifts found')
    else:
        for chemical_shift_set in enumerate(cs_result_sets):                                  # iterate over sets of shifts
            s = cs_set(chemical_shift_set[0]+1)
            for line in chemical_shift_set[1]:
                chain_name = line[0]
                res_i = int(''.join(c for c in line[1] if c.isdigit()))                       # ignore non-numeric characters
                res_name = line[2]
                atom_type = line[3]
                shift_value = float(line[4])

                if res_name in rci_nef_dicts.amino_acids_three_letter and atom_type in rci_nef_dicts.backbone_atoms:   # check that residue is a standard amino acid and atom is a backbone atom

                    if chain_name not in [c.i for c in s.chains]:            # make chain object if chain is new
                        c = chain(chain_name)
                        s.chains.append(c)

                    for c in s.chains:                                       # check if chain has residue already and make residue object if not
                        if c.i == chain_name:
                            if res_i not in [r.i for r in c.residues]:                      
                                r = res(res_i,res_name)
                                c.residues.append(r)

                            for r in c.residues:
                                if r.i == res_i and r.name == res_name:
                                    append_shift(r,atom_type,shift_value)
                                    break

            for c in s.chains:                                               # iterate over different chains
                for r in c.residues:                                                # append neighbours
                    for r2 in c.residues:                        
                        if (r2.i == r.i-1):
                            r.neighbours[0] = r2
                        if (r2.i == r.i+1):
                            r.neighbours[1] = r2

                    if r.name == 'GLY':                                             # average GLY HA shifts
                        HA = []                                                        
                        for s in r.shifts:
                            if s.atom_type in ['QA','HA1','HA2','HA3','HAx','HAy']:
                                HA.append(s.shift)
                        if HA != []:
                            r.shifts = [s for s in r.shifts if s.atom_type not in ['QA','HA1','HA2','HA3','HAx','HAy']]    
                            append_shift(r,'HA',np.mean(HA))

                for r in c.residues:                                                # compute neighbour corrected secondary shifts, apply mininum values
                    for s in r.shifts:
                        correction = 0
                        for n in enumerate(r.neighbours):
                            if n[1] != '':  
                                correction += rci_nef_dicts.RC_correction[s.atom_type][n[0]][n[1].name] 
                        r.secondary_shifts.append(atom(s.atom_type,max(rci_nef_dicts.min_shift_values[s.atom_type],np.abs(s.shift - (rci_nef_dicts.RC_values[s.atom_type][r.name] + correction)))))

                for r in c.residues:                                                # smooth secondary shifts by averaging with neighbouring shifts
                    for s in r.secondary_shifts:
                        shifts_temp = [s.shift]
                        for n in r.neighbours:
                            if n != '':
                                for ns in n.secondary_shifts:
                                    if s.atom_type == ns.atom_type:
                                        shifts_temp.append(ns.shift)
                        r.secondary_shifts_smoothed.append(atom(s.atom_type,max(0.5,rci_nef_dicts.scaling_factor[s.atom_type] * np.mean(shifts_temp))))

                    atom_list = []
                    weight_hash = ''
                    for s in r.secondary_shifts_smoothed:                           # get atom_types for weight selection 
                        atom_list.append(s.atom_type)
                    atom_list = sorted(atom_list)
                    for a in atom_list:                                             # build weight hash
                        weight_hash += a

                    RCI = 0
                    sum_weights = 0.0
                    for s in r.secondary_shifts_smoothed:
                        RCI += (10.0 * (rci_nef_dicts.RCI_weights[weight_hash][s.atom_type]) * s.shift)   # compute RCI
                        sum_weights += rci_nef_dicts.RCI_weights[weight_hash][s.atom_type]
                    r.RCI = min(sum_weights / RCI,0.2)

                    r.num_shifts = len(atom_list)                                   # count number of shifts for output file
                    r.shift_types = weight_hash                                     # shift types for output file


                min_resi = min(r.i for r in c.residues)                             # apply end correction - see Whishart RCI paper
                max_resi = max(r.i for r in c.residues)

                N_term = [r for r in c.residues if r.i in range(min_resi,min_resi+4)]
                C_term = [r for r in c.residues if r.i in range(max_resi-3,max_resi+1)]

                max_N_term_RCI = max([r.RCI for r in N_term])
                max_C_term_RCI = max([r.RCI for r in C_term])

                max_N_term_pos = [r.i for r in N_term if r.RCI == max_N_term_RCI][0]
                max_C_term_pos = [r.i for r in C_term if r.RCI == max_C_term_RCI][-1]

                for r in N_term:
                    if r.i <= max_N_term_pos:
                        r.RCI = (2*np.abs(max_N_term_RCI - r.RCI)) + r.RCI

                for r in C_term:
                    if r.i >= max_C_term_pos:
                        r.RCI = (2*np.abs(max_C_term_RCI - r.RCI)) + r.RCI


                for r in c.residues:                                                # smooth RCI by averaging ith neighbours
                    RCI = [r.RCI]
                    RCI.extend([n.RCI for n in r.neighbours if n != ''])          
                    r.RCI_smoothed = np.mean(RCI)

                    offset = 0.024                                                  # re-scale RCI based on comparisons to computed rigidity from structures
                    scale = 0.2-0.024
                    r.RCI_smoothed = min(max((r.RCI_smoothed-offset)/scale,0.0),1.0)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        valid_chains = {}
        chains_output = {}
        for s in cs_set._registry:
            for c in s.chains:
                out = open(output_dir+os.path.splitext(path_to_nef_file)[0]+"_"+c.i+"_"+str(s.i)+".rci",'w')   # splittext!
                rci = []
                x = []
                for r in c.residues:
                    x.append(int(r.i))
                    rci.append(r.RCI_smoothed)
                    out.write('{:>5}'.format(str(r.i)) + '{:>4}'.format(r.name) + ' ' + '{:<20.18f}'.format(r.RCI_smoothed) + '{:>2}'.format(r.num_shifts) +' '+ r.shift_types + '\n')
                out.close()

                if s.i not in valid_chains:
                    valid_chains[s.i] = c.i
                else:
                    valid_chains[s.i] += c.i

                if c.i not in chains_output:
                    chains_output[c.i] = [output_dir+os.path.splitext(path_to_nef_file)[0]+"_"+c.i+"_"+str(s.i)+".rci"]
                else:
                    chains_output[c.i].append(output_dir+os.path.splitext(path_to_nef_file)[0]+"_"+c.i+"_"+str(s.i)+".rci")

        msg=''
        for s in valid_chains:
            msg+= 'set '+str(s)+' [chain(s) '+valid_chains[s]+'], '
        check_quiet_print(quiet,' -> found ' +str(len(valid_chains))+ ' set(s) of shifts - '+msg[:-2])

    return chains_output



def main():

    calc_RCI(sys.argv[1])

    sys.exit(0)

      
if __name__ == "__main__":
    main()