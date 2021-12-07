#!/usr/bin/env python

import sys
import os
import json
import argparse
import shutil
import glob
import re

from ansurr import rci_nef
from ansurr import rigidipy
from ansurr import compare

from ansurr.functions import check_quiet_print

sys.tracebacklimit = 0

#def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
#    return [int(text) if text.isdigit() else text.lower()
#            for text in _nsre.split(s)]

natsort = lambda s: [int(t) if t.isdigit() else t.lower() for t in re.split('(\d+)', s)]


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--ligands", help=" include free ligands when computing flexibility", action="store_true")
    parser.add_argument("-n", "--nonstd", help=" include non-standard residues when computing flexibility", action="store_true")
    parser.add_argument("-o", "--oligomer", help="combine chains into a single structure when calculating flexibility", action="store_true")
    parser.add_argument("-q", "--quiet", help="supress output to the terminal", action="store_true")
    parser.add_argument("-p", "--pdb", type=str, help="input PDB file",required=True)
    parser.add_argument("-s", "--shifts", type=str, help="input shifts file in NEF format",required=True)
    args = parser.parse_args()

    path_to_shifts = args.shifts
    path_to_pdb = args.pdb # need to check that file looks like a PDB file
    
    shift_file = os.path.basename(os.path.splitext(path_to_shifts)[0])
    pdb_file = os.path.basename(os.path.splitext(path_to_pdb)[0])

    output_dir = os.path.join(os.getcwd(), pdb_file+'_'+shift_file)

    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
        check_quiet_print(args.quiet,"overwriting output directory: "+output_dir)
    os.makedirs(output_dir)  


    check_quiet_print(args.quiet,"calculating RCI")
    chain_output_rci = rci_nef.calc_RCI(path_to_shifts,output_dir+'/other_output/RCI/',quiet=args.quiet)

    check_quiet_print(args.quiet,'extracting models from '+path_to_pdb)
    pdbs,args.oligomer  = rigidipy.extract_pdb(path_to_pdb,output_dir,freeligands=args.ligands,nonstandardres=args.nonstd,oligomers=args.oligomer,quiet=args.quiet)
    if len(pdbs) > 0:
        check_quiet_print(args.quiet,' -> extracted '+str(len(pdbs))+' model(s)')
    else:
        check_quiet_print(args.quiet,' -> CRITICAL ERROR failed to extract any models, exiting')
        sys.exit()


    check_quiet_print(args.quiet,'computing the flexibility of each model')
    chain_output_rigidity = {}
    for pdb in sorted(pdbs,key=natsort):
        check_quiet_print(args.quiet," -> "+os.path.basename(os.path.splitext(pdb)[0]),end='')
        if rigidipy.calc_rigidity(pdb,quiet=args.quiet):
            check_quiet_print(args.quiet,' DONE')
            if args.oligomer:
                rigidipy.rigid_decomp(pdb,output_dir+'/other_output/extracted_pdbs/combined/',output_dir+'/other_output/FIRST/')
                try:
                    os.remove(output_dir+'/other_output/extracted_pdbs/combined/decomp_list')  # important to delete decomp_list
                except OSError:
                    pass
            else:
                chain_output_rigidity = rigidipy.rigid_decomp(pdb,output_dir+'/other_output/extracted_pdbs/',output_dir+'/other_output/FIRST/',chain_output=chain_output_rigidity)
                try:
                    os.remove(output_dir+'/other_output/extracted_pdbs/decomp_list')  # important to delete decomp_list
                except OSError:
                    pass
        else:
            check_quiet_print(args.quiet,' FAILED')

    if len(glob.glob(output_dir+'/other_output/FIRST/*.decomp')) == 0: # check FIRST worked
        check_quiet_print(args.quiet,' -> CRITICAL ERROR FIRST failed to run for any models, exiting')
        sys.exit(0)

    if args.oligomer:
        for pdb in glob.glob(output_dir+"/other_output/FIRST/*.decomp"):
            chain_output_rigidity = rigidipy.split_decomp(pdb,pdb_file,output_dir+"/other_output/FIRST/",chain_output_rigidity)
            os.remove(pdb)

        try:
            os.remove("resi_ref.tmp")
        except:
            pass

    #    json.dump(chain_output_rigidity, open("chain_output_rigidity.tmp",'w'))
    #json.dump(chain_output_rci, open("chain_output_rci.tmp",'w'))

    decomps = glob.glob(output_dir+'/other_output/FIRST/*.decomp')

    check_quiet_print(args.quiet,'computing ANSURR scores')
    
    #for decomp in sorted(decomps,key=natsort):
    #    for rci in glob.glob(output_dir+'/other_output/RCI/*.rci'):
    #        compare.compare_rci_rigidity(decomp,rci,output_dir+'/ANSURR_output/')

    for chain in chain_output_rigidity:
        for rigidity in sorted(chain_output_rigidity[chain],key=natsort):
            if chain != ' ':
                for rci in sorted(chain_output_rci[chain],key=natsort):
                    compare.compare_rci_rigidity(rigidity,rci,output_dir+'/ANSURR_output/',quiet=args.quiet)
            else:
                for rci_chain in sorted(chain_output_rci,key=natsort):
                    for rci in chain_output_rci[rci_chain]:
                        compare.compare_rci_rigidity(rigidity,rci,output_dir+'/ANSURR_output/',quiet=args.quiet)  


    check_quiet_print(args.quiet,"summary of ANSURR scores")
    for line in open(output_dir+'/ANSURR_output/scores.out','r'):
        check_quiet_print(args.quiet," -> "+line.strip())

    sys.exit(0)

      
if __name__ == "__main__":
    main()

