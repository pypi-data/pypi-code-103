#!/usr/bin/env python3

"""Module containing the ExtractHeteroAtoms class and the command line interface."""
import argparse
import re
# import warnings
from pathlib import Path
from biobb_common.configuration import settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from Bio import BiopythonWarning
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB.PDBIO import PDBIO
#from Bio.PDB.PDBIO import Select
#from Bio.PDB.StructureBuilder import StructureBuilder
from Bio.PDB import Dice
from biobb_structure_utils.utils.common import *

#res_id = ''

class ExtractHeteroAtoms():
    """Class to extract a list of heteroatoms from a 3D structure.

    Args:
        input_structure_path (str): Input structure file path. Accepted formats: pdb.
        output_heteroatom_path (str): Output heteroatom file path. Accepted formats: pdb.
        properties (dic):
            * **heteroatoms** (*list*) - (None) List of dictionaries with the name | res_id | chain | model of the heteroatoms to be extracted. Format: [{"name": "ZZ7", "res_id": "302", "chain": "B", "model": "1"}]. If empty, all the heteroatoms of the structure will be returned.
    """

    def __init__(self, input_structure_path, output_heteroatom_path, properties=None, **kwargs):
        properties = properties or {}

        # Input/Output files
        self.input_structure_path = str(input_structure_path)
        self.output_heteroatom_path = str(output_heteroatom_path)

        # Properties specific for BB
        self.check_structure_path = properties.get('check_structure_path', 'check_structure')
        self.heteroatoms = properties.get('heteroatoms', [])
        self.properties = properties

        # Common in all BB
        self.can_write_console_log = properties.get('can_write_console_log', True)
        self.global_log = properties.get('global_log', None)
        self.prefix = properties.get('prefix', None)
        self.step = properties.get('step', None)
        self.path = properties.get('path', '')
        self.remove_tmp = properties.get('remove_tmp', True)
        self.restart = properties.get('restart', False)

    def check_data_params(self, out_log, err_log):
        """ Checks all the input/output paths and parameters """
        self.input_structure_path = check_input_path(self.input_structure_path, out_log, self.__class__.__name__)
        self.output_heteroatom_path = check_output_path(self.output_heteroatom_path, out_log, self.__class__.__name__)

    def check_format_heteroatoms(self, hets, out_log):
        """ Check format of heteroatoms list """
        if not hets:
            return 0
        
        listh = []

        for het in hets:
            d = het
            code = []
            if 'name' in het: code.append('name')
            if 'res_id' in het: code.append('res_id')
            if 'chain' in het: code.append('chain')
            if 'model' in het: code.append('model')

            d['code'] = code
            listh.append(d)

        return listh


    @launchlogger
    def launch(self):
        """Remove ligand atoms from the structure."""
        tmp_files = []

        # Get local loggers from launchlogger decorator
        out_log = getattr(self, 'out_log', None)
        err_log = getattr(self, 'err_log', None)

        # check input/output paths and parameters
        self.check_data_params(out_log, err_log)

        # Check the properties
        fu.check_properties(self, self.properties)

        #Restart if needed
        if self.restart:
            output_file_list = [self.output_structure_path]
            if fu.check_complete_files(output_file_list):
                fu.log('Restart is enabled, this step: %s will the skipped' % self.step,  out_log, self.global_log)
                return 0

        #################################################
        #################################################
        # warnings.simplefilter('ignore', BiopythonWarning)
        #################################################
        #################################################

        list_heteroatoms = self.check_format_heteroatoms(self.heteroatoms, out_log)

        structure = PDBParser(QUIET = True).get_structure('structure', self.input_structure_path)

        if not list_heteroatoms:
            fu.log('Empty list of heteroatoms or incorrect format, all the heteroatoms of the structure will be selected', out_log)

        #new_structure = Select()
        #new_structure = PDBParser(QUIET = True).get_structure('heteroatom', None)
        #new_structure = PDBParser(QUIET = True)

        new_structure = []

        for residue in structure.get_residues():

            #if not residue.get_resname() in PDB_WATERS:

            r = {
                'model': str(residue.get_parent().get_parent().get_id() + 1),
                'chain': residue.get_parent().get_id(),
                'name': residue.get_resname(),
                'res_id': str(residue.get_id()[1])
            }

            
            for het in list_heteroatoms:
                match = True
                for code in het['code']:
                    if het[code].strip() != r[code].strip():
                        match = False
                        break

                if(match): 
                    #print(residue)
                    new_structure.append(residue)

                # *********************************************

                """if match: 
                    print(r['chain'], int(r['res_id']), int(r['res_id']), self.output_heteroatom_path)
                    dice = Dice.extract(structure, r['chain'], int(r['res_id'])-1, int(r['res_id'])+1, self.output_heteroatom_path)"""

                """if not match:
                    print("remove", residue.id)
                    residue.get_parent().detach_child(residue.id)
                else:
                    print("preserve", residue.id)"""

                #print(residue.get_parent().get_id())
                #residue.detach_parent()
                """res_id = str(residue.get_id()[1])
                class ResSelect(Select):
                    print(res_id)
                    def accept_residue(self, res):
                        #print(res_id)
                        #print(match)
                        #print(residue, match)
                        #print(self.input_structure_path)
                        if match:
                            return 1
                        else:
                            return 0
                        #print(res.get_id())
                        if str(res.get_id()[1]) == res_id:
                            return 1
                        else:
                            return 0"""

                """if(match): 
                    print(residue)
                    #new_structure.accept_residue(res)
                    #new_structure.init_residue(r['name'], 'H', r['res_id'], '0')
                    class ResSelect(Select):
                        def accept_residue(self, res):
                            if res.get_resname() == 'GLY':
                                return 1
                            else:
                                return 0"""

        #print(structure)

        #exit()

        for residue in structure.get_residues():
            #print(ns.get_id())

            if(not residue in new_structure):
                #residue.get_parent().detach_child(residue.id)
                structure.detach_child(residue.id)


        io = PDBIO()
        io.set_structure(structure) 
        io.save(self.output_heteroatom_path)
        print('Saved in ' + self.output_heteroatom_path)

        """num_models = len(list(structure.get_models()))

        if(num_models > 1):

            for model in structure.get_models():
                print(model.get_id())

        else:

            num_chains = len(list(structure.get_chains()))
            print(num_chains)"""


        # if check_format == 0, seleccionar-los tots, 


        """model = structure[0]
        chain = model['A']
        residues = [1,2,3,4,5]
        for i in residues:
            #print (chain[i].resname)
            print(chain[i])"""

        # https://biopython.org/DIST/docs/api/Bio.PDB.Structure.Structure-class.html

        # descartar aigües: SOL HOH WAT T3P

        # si self.heteroatoms està buit, faig només get residues menys aigües
        # si només name trec tots els res_name
        # si res_id, els que tinguin res_id
        # si chain, itero primer les cadenes
        # si model i chain, itero primer models i després cadenes

        # CHECK FORMAT!!! què passa si no chain? name.res_id:/model; Si no model? name.res_id:chain/ o  name.res_id:chain

        """
        OOKKKKKKKKK!!!
        for model in structure.get_models():
            print(model.get_id())
        """

        """
        OOKKKKKKKKK!!!
        for chain in structure.get_chains():
            print(chain.get_id())
        """

        """
        OOKKKKKKKKK!!!
        for res in structure.get_residues():
            print(res.get_resname())"""

        return 0

def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(description="Extract a list of heteroatoms from a 3D structure.", formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('-c', '--config', required=False, help="This file can be a YAML file, JSON file or JSON string")
    parser.add_argument('--system', required=False, help="Check 'https://biobb-common.readthedocs.io/en/latest/system_step.html' for help")
    parser.add_argument('--step', required=False, help="Check 'https://biobb-common.readthedocs.io/en/latest/system_step.html' for help")

    #Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('-i', '--input_structure_path', required=True, help="Input structure file path. Accepted formats: pdb.")
    required_args.add_argument('-o', '--output_heteroatom_path', required=True, help="Output heteroatom file path. Accepted formats: pdb.")

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config, system=args.system).get_prop_dic()
    if args.step:
        properties = properties[args.step]

    #Specific call of each building block
    ExtractHeteroAtoms(input_structure_path=args.input_structure_path, output_heteroatom_path=args.output_heteroatom_path, properties=properties).launch()

if __name__ == '__main__':
    main()
