#!/usr/bin/env python3
# -*- coding:utf-8 -*- import numpy as np import re
import argparse
import collections
import re
import os
from natf.cell import get_cell_index, Cell, get_cell_index_by_mid
from natf.utils import is_blank_line, log
from natf import mcnp_input


def is_tally_result_start(line, tally_num=None):
    """
    Check whether a line is the tally result start.

    Parameters:
    -----------
    line: str
        The line to be checked.
    tally_num: int or None
        None: Check this is the start of any tally
        int: Check for the specific tally number.
    """
    tally_start_pattern = re.compile("^1tally .*nps =", re.IGNORECASE)
    if re.match(tally_start_pattern, line):
        # check tally id
        if tally_num is None:
            return True
        else:
            return get_tally_id(line) == tally_num
    else:
        return False


def is_tally_result_end(line):
    tally_end_pattern1 = re.compile(".*tfc bin check", re.IGNORECASE)
    tally_end_pattern2 = re.compile(".*===", re.IGNORECASE)
    if re.match(tally_end_pattern1, line) or re.match(tally_end_pattern2, line):
        return True
    else:
        return False


def get_tally_id(line):
    if not is_tally_result_start(line):
        raise ValueError(f"line: {line} is not tally result start")
    line_ele = line.strip().split()
    return int(line_ele[1])


def has_tally_result(filename, tally_num=[4]):
    """Check whether the file contain specific tally result"""
    if filename is None or filename == '':
        return False
    if not os.path.isfile(filename):
        return False
    if isinstance(tally_num, int):
        tally_num = [tally_num]
    with open(filename, 'r') as fin:
        while True:
            line = fin.readline()
            if line == '':
                return False
            if is_tally_result_start(line):
                if get_tally_id(line) in tally_num:
                    return True
    return False


def get_tally_file(MCNP_OUTPUT, CONTINUE_OUTPUT, TALLY_NUMBER):
    """
    Check which file to use when both MCNP_OUTPUT and CONTINUE_OUTPUT are provided.
    """
    # check tally results
    if has_tally_result(MCNP_OUTPUT, TALLY_NUMBER) and \
            not has_tally_result(CONTINUE_OUTPUT, TALLY_NUMBER):
        return MCNP_OUTPUT
    if has_tally_result(CONTINUE_OUTPUT, TALLY_NUMBER):
        print(f"Tally {TALLY_NUMBER} results in {CONTINUE_OUTPUT} will be used")
        return CONTINUE_OUTPUT
    if not has_tally_result(MCNP_OUTPUT, TALLY_NUMBER) and \
            not has_tally_result(CONTINUE_OUTPUT, TALLY_NUMBER):
        raise ValueError(
            f"ERROR: {MCNP_OUTPUT} and {CONTINUE_OUTPUT} do not have tally result")


def get_cell_names_from_line(line):
    """
    """
    cell_names = []
    ls = line.strip().split()
    for i in range(1, len(ls)):
        cell_names.append(int(ls[i]))
    return cell_names


def read_tally_result_single_cell_single_group(filename, tally_num=4, with_fm=False):
    """
    Get the result for a tally that has only single cell, single energy group and with FM card.
    This can be used for the tbr calculation for new tallies.

    Parameters:
    -----------
    filename: str
        the mcnp output file to be read
    TALLY_NUMBER: int
        tally number
    """
    cids, results, errs = [], [], []
    fin = open(filename)
    while True:
        line = fin.readline()
        if line == '':
            raise ValueError(
                f'1tally {tally_num} not found in the file, wrong file!')
        if not is_tally_result_start(line):
            continue
        if get_tally_id(line) == tally_num:
            while True:
                line1 = fin.readline()
                line_ele1 = line1.split()
                if is_blank_line(line1):
                    continue
                if is_tally_result_end(line1):
                    break
                if " cell " in line1:
                    cid = get_cell_names_from_line(line1)
                    cids.extend(cid)
                    line = fin.readline()
                    if with_fm:
                        line = fin.readline()
                    line_ele = line.split()
                    for j in range(len(cid)):
                        results.append(float(line_ele[2 * j]))
                        errs.append(float(line_ele[2 * j + 1]))
            break
    fin.close()
    return cids, results, errs


def read_tally_result_single_group(filename, tally_num=4):
    """
    Get the single group neutron flux for a tally.
    This is used for the volume calculation.

    Parameters:
    -----------
    filename: str
        the mcnp output file to be read
    TALLY_NUMBER: int
        tally number
    """
    cids, results, errs = [], [], []
    fin = open(filename)
    while True:
        line = fin.readline()
        if line == '':
            raise ValueError(
                f'1tally {tally_num} not found in the file, wrong file!')
        if not is_tally_result_start(line):
            continue
        if get_tally_id(line) == tally_num:
            while True:
                line1 = fin.readline()
                line_ele1 = line1.split()
                if is_blank_line(line1):
                    continue
                if is_tally_result_end(line1):
                    break
                if " cell " in line1:
                    cid = get_cell_names_from_line(line1)
                    cids.extend(cid)
                    line = fin.readline()
                    line_ele = line.split()
                    for j in range(len(cid)):
                        results.append(float(line_ele[2 * j]))
                        errs.append(float(line_ele[2 * j + 1]))
            break
    fin.close()
    return cids, results, errs


def read_cell_neutron_flux_single_tally(filename, tally_num=4, N_GROUP_SIZE=175):
    """
    Get the neutron flux for a single tally.

    Parameters:
    -----------
    filename: str
        the mcnp output file to be read
    TALLY_NUMBER: int
        tally number
    N_GROUP_SIZE: int
        Number of group size, 69, 175, 315 or 709.
    """
    cids, fluxes, errs = [], [], []
    fin = open(filename)
    while True:
        line = fin.readline()
        if line == '':
            raise ValueError(
                f'1tally {tally_num} not found in the file, wrong file!')
        if not is_tally_result_start(line):
            continue
        if get_tally_id(line) == tally_num:
            while True:
                line1 = fin.readline()
                line_ele1 = line1.split()
                if is_blank_line(line1):
                    continue
                # end of the cell neutron flux information part
                if is_tally_result_end(line1):
                    break
                if 'cell' in line1:
                    line2 = fin.readline()
                    if 'energy' in line2:  # the folowing 176/710 lines are neutron flux information
                        cid = get_cell_names_from_line(line1)
                        cids.extend(cid)
                        cell_flux = []
                        cell_error = []
                        if N_GROUP_SIZE >= 2:
                            num_data = N_GROUP_SIZE + 1
                        else:
                            raise ValueError(
                                f"Wrong N_GROUP_SIZE:{N_GROUP_SIZE}")
                        for i in range(num_data):
                            line = fin.readline()
                            # check the neutron energy group
                            if i == N_GROUP_SIZE:
                                if 'total' not in line:
                                    errormessage = ''.join(
                                        [
                                            'ERROR in reading cell neutron flux\n',
                                            'Neutron energy group is ',
                                            str(N_GROUP_SIZE),
                                            ' in input file\n',
                                            'But keyword: \'total\' not found in the end!\n',
                                            'Check the neutron energy group in the output file\n'])
                                    raise ValueError(errormessage)
                            line_ele = line.split()
                            erg_flux = []
                            erg_error = []
                            for j in range(len(cid)):
                                erg_flux.append(float(line_ele[2 * j + 1]))
                                erg_error.append(float(line_ele[2 * j + 2]))
                            cell_flux.append(erg_flux)
                            cell_error.append(erg_error)
                        for i in range(len(cid)):
                            temp_flux = []
                            temp_error = []
                            for j in range(num_data):
                                temp_flux.append(cell_flux[j][i])
                                temp_error.append(cell_error[j][i])
                            fluxes.append(temp_flux)
                            errs.append(temp_error)
            break
    fin.close()
    print(f"finish reading neutron flux from {filename} tally {tally_num}")
    return cids, fluxes, errs


def tallied_vol_to_tally(inp="outp", output="tally_card.txt"):
    """
    Read the f4 tally for volume, get the cids, vols, errs info and write
    tally card.
    """
    tallied_vol_to_tally_help = ('This script read a volume tally output file and\n'
                                 'return a tally style string.\n')

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=False,
                        help="output of the vol tally file path")
    parser.add_argument("-o", "--output", required=False,
                        help="save the tally_card to output file")
    parser.add_argument("-t", "--tally_num", required=False,
                        help="the tally number of volume info, default:4")
    args = vars(parser.parse_args())

    outp_file = "input"
    if args['input'] is not None:
        outp_file = args['input']

    tally_num = 4
    if args['tally_num'] is not None:
        tally_num = int(args['tally_num'])

    cids, vols, errs = read_tally_result_single_group(
        outp_file, tally_num=tally_num)
    # save data into a tally style card
    output = "tally_card.txt"
    if args['output'] is not None:
        output = args['output']
    mcnp_input.mcnp_tally_style(cids, sds=vols, output=output)


def update_cell_flux(cells, cids, fluxes):
    """
    Update the cell volume according to the given cids and volumes.
    """
    for i in range(len(cids)):
        cidx = get_cell_index(cells, cids[i])
        cells[cidx].neutron_flux = fluxes[i]
    return cells


@log
def get_cell_neutron_flux(MCNP_OUTPUT, cells, TALLY_NUMBER, N_GROUP_SIZE, CONTINUE_OUTPUT=None):
    """get_cell_neutron_flux: read the mcnp output file and get the neutron flux of the cell

    Parameters:
    -----------
    MCNP_OUTPUT: str
        the mcnp output file
    cells: list
        the list of Cell
    TALLY_NUMBER: int
        tally number
    N_GROUP_SIZE: int
        Number of group size, 69, 175, 315 or 709.
    CONTINUE_OUTPUT: str, optional
       The output file of continue run, contains neutron flux info. Used when
       the MCNP_OUTPUT file does not contian neutron flux info.

    Returns:
    --------
    cells: list
        cells that have the neutron flux information in it
    """
    tally_file = get_tally_file(MCNP_OUTPUT, CONTINUE_OUTPUT, TALLY_NUMBER)
    if isinstance(TALLY_NUMBER, int):
        cids, fluxes, errs = read_cell_neutron_flux_single_tally(
            tally_file, TALLY_NUMBER, N_GROUP_SIZE)
        cells = update_cell_flux(cells, cids, fluxes)
    elif isinstance(TALLY_NUMBER, list):
        for i in range(len(TALLY_NUMBER)):
            cids, fluxes, errs = read_cell_neutron_flux_single_tally(
                tally_file, TALLY_NUMBER[i], N_GROUP_SIZE)
            cells = update_cell_flux(cells, cids, fluxes)
    print('     read cell neutron flux over')
    return cells


def read_cell_vol_single_tally(filename, tally_num):
    """
    Read the cell, volume and mass information for specific tally.
    """
    cids, vols = [], []
    with open(filename, 'r') as fin:
        while True:
            line = fin.readline()
            if line == '':
                raise ValueError(
                    f'tally result not found in the file, wrong file!')
            if is_tally_result_start(line, tally_num):
                # read the following line
                line = fin.readline()
                line = fin.readline()
                line = fin.readline()
                line = fin.readline()
                while True:
                    line = fin.readline()
                    line_ele = line.split()
                    if len(line_ele) == 0:  # end of the volumes
                        break
                    # otherwise, there are volume information
                    if line_ele[0] == 'cell:':  # this line contains cell names
                        cell_names = get_cell_names_from_line(line)
                        line = fin.readline()  # this is the volume information
                        line_ele = line.split()
                        cell_vols = get_cell_vols_from_line(line)
                        cids.extend(cell_names)
                        vols.extend(cell_vols)
                break
    return cids, vols


def update_cell_vol(cells, cids, vols):
    """
    Update the cell volume according to the given cids and volumes.
    """
    for i in range(len(cids)):
        cidx = get_cell_index(cells, cids[i])
        cells[cidx].vol = vols[i]
    return cells


@log
def get_cell_vol_mass(MCNP_OUTPUT, cells, TALLY_NUMBER, CONTINUE_OUTPUT=None):
    """get_cell_vol_mass, read the mcnp output file and get the volumes and masses of the cells"""
    # open the mcnp output file
    tally_file = get_tally_file(MCNP_OUTPUT, CONTINUE_OUTPUT, TALLY_NUMBER)
    if isinstance(TALLY_NUMBER, int):
        cids, vols = read_cell_vol_single_tally(tally_file, TALLY_NUMBER)
        cells = update_cell_vol(cells, cids, vols)
    elif isinstance(TALLY_NUMBER, list):
        for i in range(len(TALLY_NUMBER)):
            cids, vols = read_cell_vol_single_tally(
                tally_file, TALLY_NUMBER[i])
            cells = update_cell_vol(cells, cids, vols)
    # calculate the mass of the cells
    for c in cells:
        if c.vol > 0:
            c.mass = c.density * c.vol
    return cells


@log
def get_cell_tally_info(MCNP_OUTPUT, cells, TALLY_NUMBER, N_GROUP_SIZE,
                        CONTINUE_OUTPUT=None):
    """get_cell_tally_info: run this only for the cell tally condition"""
    cells = get_cell_vol_mass(MCNP_OUTPUT, cells, TALLY_NUMBER,
                              CONTINUE_OUTPUT=CONTINUE_OUTPUT)
    cells = get_cell_neutron_flux(MCNP_OUTPUT, cells, TALLY_NUMBER,
                                  N_GROUP_SIZE, CONTINUE_OUTPUT=CONTINUE_OUTPUT)
    return cells


def get_cell_vols_from_line(line):
    cell_vols = []
    ls = line.strip().split()
    for i in range(len(ls)):
        cell_vols.append(float(ls[i]))
    return cell_vols


def is_cell_info_start(line):
    """
    Check if this line is the cells info start.
    """
    # This check works for MCNP5 1.2
    if "cells" in line and "print table 60" in line:
        return True
    else:
        return False


@log
def get_cell_icl_cellid_matid_matdensity(MCNP_OUTPUT, cells):
    """get_cell_icl_cellid_matid
    input parameter: MCNP_OUTPUT, the path of the mcnp output file
    return: cells[], a list of cells"""

    fin = open(MCNP_OUTPUT, 'r')
    while True:
        line = fin.readline()
        if line == '':
            raise ValueError('1cells not found in the file, wrong file!')
        if is_cell_info_start(line):  # read 1cells
            # read the following line
            line = fin.readline()
            line = fin.readline()
            line = fin.readline()
            line = fin.readline()
            while True:
                temp_c = Cell()
                line = fin.readline()
                if ' total' in line:  # end of the cell information part
                    break
                # check data
                line_ele = line.split()
                if len(line_ele) == 0:  # skip the blank line
                    continue
                if str(line_ele[0]).isdigit():  # the first element is int number
                    icl, cid, mid, density = int(
                        line_ele[0]), int(
                        line_ele[1]), int(
                        line_ele[2]), float(
                        line_ele[4])
                    temp_c.icl, temp_c.id, temp_c.mid, temp_c.density = icl, cid, mid, density
                cells.append(temp_c)
            break
    fin.close()
    return cells


@log
def get_cell_basic_info(MCNP_OUTPUT):
    """get_cell_info: get the cell information
     include icl, cid, mid, density"""
    cells = []
    # get icl, cid, mid, density
    cells = get_cell_icl_cellid_matid_matdensity(MCNP_OUTPUT, cells)
    return cells


def get_mid_nucs_fracs(line):
    """
    Get the material id, nuclide list and fraction.
    """
    tokens = line.strip().split()
    mid = int(tokens[0])
    nucs, fracs = [], []
    for i in range(1, len(tokens), 2):
        nucs.append(tokens[i][:-1])
        fracs.append(float(tokens[i+1]))
    return mid, nucs, fracs


def get_nucs_fracs(line):
    """
    Get the material nuclide list and fraction.
    """
    tokens = line.strip().split()
    nucs, fracs = [], []
    for i in range(0, len(tokens), 2):
        nucs.append(tokens[i][:-1])
        fracs.append(float(tokens[i+1]))
    return nucs, fracs


def get_material_basic_info(MCNP_OUTPUT):
    """
    Get the basic information of the material.
    - mat_number
    - density
    - nuc_vec: dict of nuclide/mass_fraction pair
    """
    cells = get_cell_basic_info(MCNP_OUTPUT)
    # get used materials ids
    mids, densities, nuc_vecs = [], [], []
    mid = 0
    # read material composition
    with open(MCNP_OUTPUT, 'r', encoding='utf-8') as fin:
        while True:
            line = fin.readline()
            if line == '':
                raise ValueError("material composition not found in the file")
            if 'number     component nuclide, mass fraction' in line:  # start of material composition
                while True:
                    line = fin.readline()
                    if 'cell volumes and masses' in line:  # end of material composition
                        # save the last material
                        mids.append(mid)
                        cidx = get_cell_index_by_mid(cells, mid)
                        densities.append(cells[cidx].density)
                        nuc_vecs.append(nuc_vec)
                        break
                    if is_blank_line(line) or 'warning' in line:
                        continue
                    tokens = line.strip().split()
                    if len(tokens) % 2 != 0:  # this line contain mid
                        if mid > 0:  # not the first material, save the previous one
                            mids.append(mid)
                            cidx = get_cell_index_by_mid(cells, mid)
                            densities.append(cells[cidx].density)
                            nuc_vecs.append(nuc_vec)
                        nuc_vec = {}
                        mid, nucs, fracs = get_mid_nucs_fracs(line)
                    else:  # this line do not have mid
                        nucs, fracs = get_nucs_fracs(line)
                    # update the nuc_vec
                    for i, nuc in enumerate(nucs):
                        if nuc not in nuc_vec.keys():
                            nuc_vec[nuc] = fracs[i]
                        else:
                            nuc_vec[nuc] += fracs[i]
                break
    return mids, densities, nuc_vecs


def get_tbr_from_mcnp_output(filename, tallies):
    """
    Read the MCNP output file to get the tbr.
    The TBR for each breeder cells may distributed in difference tallies.

    Parameters:
    -----------
    filename: str
        The MCNP output file.
    tallies: list of int
        The tally number that contains TBR information.
    """
    tbr_total = 0.0
    for tid in tallies:
        cids, tbr_tmps, errs = read_tally_result_single_cell_single_group(
            filename, tally_num=tid, with_fm=True)
        tbr_total += tbr_tmps[0]
    return tbr_total
