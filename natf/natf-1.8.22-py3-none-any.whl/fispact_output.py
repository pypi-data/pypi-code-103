#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import numpy as np
import argparse
import collections
import re
import math
from natf import utils
from natf import material

# constant variables
fispact_nuc_flag = ('?', '&', '*', '>', '#')


def contain_fispact_nuc_flag(line):
    """return True if the line contains a fispact_nuc_flag: ?,&,*,>,#
    otherwise, return False"""
    for item in fispact_nuc_flag:
        if item in line:
            return True
    return False


def is_interval_line(line):
    """Check whether this line contains interval information"""
    if 'TIME INTERVAL' not in line or 'ELAPSED TIME IS' not in line:
        return False
    else:
        return True


def found_interval_line(line, interval_list):
    """found_interval_line: judege whether this line is the line we need according to the interval list"""
    if is_interval_line(line):
        for interval in interval_list:
            if is_interval_in_line(interval, line):
                return True
    else:
        return False
    return False


def get_interval_from_line(line):
    """
    Get interval index (an integer number) from line.
    """
    ls = line.strip().split('*')
    ls = [i for i in ls if (i and i != ' ')]
    interval = ls[1].strip().split('TIME INTERVAL')[-1].strip()
    return int(interval)


def is_interval_in_line(interval, line):
    """Check whether an interval number in line.

    Parameters:
    -----------
    interval: int
        The interval number
    line: str
        The line.
    """

    if not is_interval_line(line):
        return False
    if get_interval_from_line(line) == interval:
        return True
    else:
        return False


def check_cooling_start(line, cooling_start=False):
    """
    Check wether the cooling started.
    """
    if "of steps" in line:
        return True
    else:
        return cooling_start


def get_interval_list(filename, cooling_only=False, irradiation_only=False):
    """get_interval_list, returns the interval number of the irradiation scenario."""
    # start to get the information
    interval_irrad, interval_cooling = [], []
    cooling_start = False
    with open(filename) as fin:
        #file_interval_number = 0
        for line in fin:
            if line == '':
                errormessage = ''.join(
                    ['File: ', filename, ' does not have interval message, incomplete file!'])
                raise ValueError(errormessage)
            cooling_start = check_cooling_start(line, cooling_start)
            if 'TIME INTERVAL' in line and 'ELAPSED TIME IS' in line:
                interval = get_interval_from_line(line)
                if 'COOLING TIME' in line and cooling_start:
                    # cooling phase
                    interval_cooling.append(interval)
                else:
                    # irradiation phase
                    interval_irrad.append(interval)
            if 'fispact run time=' in line:
                break
    if cooling_only:
        return interval_cooling
    if irradiation_only:
        return interval_irrad
    return interval_irrad + interval_cooling


def parser_fispact_out_nuc(string):
    """
    Parser the nuclide identifier from a string in fispact output file.
    """
    tokens = string.strip().split()
    if len(tokens) == 1:
        return tokens[0]
    elif len(tokens) == 2:
        return f"{tokens[0]}{tokens[1]}"
    else:
        raise ValueError(f"wrong string {string} for nuclide name parsering")


def parser_fispact_out_data(string):
    """
    Parser the nuclide identifier from a string in fispact output file.
    """
    line_ele = string.strip().split()
    atoms, act, contact_dose, ci = map(
        float, [line_ele[0], line_ele[2], line_ele[6], line_ele[9]])
    decay_heat = sum(map(float, [line_ele[3], line_ele[4], line_ele[5]]))
    if line_ele[-1].lower() == 'stable':
        half_life = float('inf')
    else:
        half_life = float(line_ele[-1])
    return atoms, act, contact_dose, ci, half_life, decay_heat


def get_fispact_out_line_info(line):
    """return nuc, act,dose_rate, ci, half_life of a line
    # a line of fispact output of nuclides, contains several information, a sample line like below
    #  NUCLIDE        ATOMS         GRAMS        Bq       b-Energy    a-Energy   g-Energy    DOSE RATE   INGESTION  INHALATION   CLEARANCE     Bq/A2     HALF LIFE
    #                                                    kW          kW         kW         Sv/hr      DOSE(Sv)    DOSE(Sv)     INDEX       Ratio      seconds
    #H   3       6.72510E+21   3.368E-02   1.198E+13   1.095E-05   0.00E+00   0.000E+00   0.000E+00   5.032E+02   3.115E+03   1.198E+08   2.995E-01   3.891E+08
    #K  40     > 5.85721E+17   3.887E-05   1.017E+01   7.387E-16   0.00E+00   2.538E-16   3.850E-10   6.306E-08   2.136E-08   1.017E-03   1.130E-11   3.992E+16
    #Rh104m      2.85761E+14   4.931E-08   7.607E+11   1.051E-05   0.00E+00   5.548E-06   7.358E-01   6.694E+00   6.009E+00   4.226E+07   3.803E+01   2.604E+02
    #Rh104m    > 2.85761E+14   4.931E-08   7.607E+11   1.051E-05   0.00E+00   5.548E-06   7.358E-01   6.694E+00   6.009E+00   4.226E+07   3.803E+01   2.604E+02
    #H   1    #> 6.57716E+23   1.101E+00   0.000E+00   0.000E+00   0.00E+00   0.000E+00   0.000E+00   0.000E+00   0.000E+00   0.000E+00   0.000E+00     Stable
    #Hg199  ? #  1.34828E+13   4.455E-09   0.000E+00   0.000E+00   0.00E+00   0.000E+00   0.000E+00   0.000E+00   0.000E+00   0.000E+00   0.000E+00     Stable
    # if a line doesn't contain a flag of ?,&,*,>, then the nuclide should be in the first one or two element
    # if a first element of a line contains less than 3 character, that means the nuclide distributed in two parts
    # there are 4 kinds of conditons,
    # case A: nuclide name in two part, no flag
    # case B: nuclide name in two part, with flag
    # case C: nuclide name in one part, no flag
    # case D: nuclide name in one part, with flag
    # case E: nuclide name in two part, with flag
    # case F: nuclide name in one part, with two separated flags

    Output:
    -------
    nuc, atoms, act, contact_dose, ci, half_life, decay_heat
    """
    line = line.strip()
    line_ele = line.split()
    if len(line_ele) < 12:  # this line must be wrong
        errormessage = ''.join(
            ['line:', line, 'have wrong information, check!'])
        raise ValueError(errormessage)
    nuc = parser_fispact_out_nuc(line[0:6])
    atoms, act, contact_dose, ci, half_life, decay_heat = parser_fispact_out_data(
        line[12:])
    return nuc, atoms, act, contact_dose, ci, half_life, decay_heat


def read_fispact_out_act(c, filename, interval_list):
    """read_fispact_out_act, read the act information,
     include: nuclide, half_life, specific activity, decay heat density, ci, contact dose.
    Parameters:
    c : cell
    filename: FISPACT output file of this cell
    interval_list : clumulated cooling times
     """
    # read the file first time to get the nuclide and half_life
    nuclide = []
    half_life = []
    fin = open(filename)
    while True:
        line = fin.readline()
        if 'fispact run time' in line:  # end of the file information
            break
        if found_interval_line(line, interval_list):  # found a interval
            line = fin.readline()
            line = fin.readline()
            line = fin.readline()
            while True:
                line = fin.readline()
                if 'TOTAL NUMBER' in line:  # fp ound the end of this interval part
                    break
                nuc, atoms, act, contact_dose, ci, hf_lf, dh = get_fispact_out_line_info(
                    line)
                if nuc not in nuclide:
                    nuclide.append(nuc)
                    half_life.append(hf_lf)
    fin.close()
    c.nuclide = nuclide
    c.half_life = half_life
    # read the information in each interval, then get the  act, contact_dose,
    # ci of each nuclide
    c.act = np.resize(c.act, (len(interval_list), len(nuclide)))
    c.contact_dose = np.resize(
        c.contact_dose, (len(interval_list), len(nuclide)))
    c.decay_heat = np.resize(c.decay_heat, (len(interval_list), len(nuclide)))
    c.ci = np.resize(c.ci, (len(interval_list), len(nuclide)))
    c.total_alpha_act = np.resize(c.total_alpha_act, (len(interval_list)))
    for intv in range(len(interval_list)):
        fin = open(filename)
        while True:
            line = fin.readline()
            if is_interval_in_line(interval_list[intv], line):
                line = fin.readline()
                line = fin.readline()
                line = fin.readline()
                nuclide_end = False
                while True:
                    line = fin.readline()
                    if 'TOTAL NUMBER' in line:  # end of this interval of nuclide information
                        nuclide_end = True
                    if 'ALPHA BECQUERELS' in line and nuclide_end:
                        c.total_alpha_act[intv] = get_total_alpha_act(line)
                        break
                    if not nuclide_end:
                        nuc, atoms, act, contact_dose, ci, hf_lf, dh = get_fispact_out_line_info(
                            line)
                        nuc_index = nuclide.index(nuc)
                        c.act[intv][nuc_index] = act
                        c.decay_heat[intv][nuc_index] = dh
                        c.contact_dose[intv][nuc_index] = contact_dose
                        c.ci[intv][nuc_index] = ci
                break
        fin.close()


def get_total_alpha_act(line):
    """
    Read the total alpha activity from line.
    """
    ls = line.strip().split()
    alpha_act = utils.str2float(ls[4])
    return alpha_act


def read_fispact_out_sdr(c, filename, interval_list):
    """read_fispact_out_sdr, read the sdr information of a cell or a mesh
    include: gamma emit rate at different cooling time"""
    c.gamma_emit_rate = np.resize(c._gamma_emit_rate, (len(interval_list), 24))
    for intv in range(len(interval_list)):
        fin = open(filename)
        while True:
            line = fin.readline()
            if is_interval_in_line(interval_list[intv], line):
                while True:
                    line = fin.readline()
                    if 'GAMMA SPECTRUM AND ENERGIES' in line:
                        line = fin.readline()
                        line = fin.readline()
                        line = fin.readline()
                        line = fin.readline()
                        line = fin.readline()
                        line = fin.readline()
                        for i in range(24):  # read 24 group photon emmit rate
                            line = fin.readline()
                            line_ele = line.split()
                            c.gamma_emit_rate[intv][i] = utils.str2float(
                                line_ele[-1])
                        break  # end of gamma emit rate data
                break
        fin.close()


def read_fispact_out_dpa(c, filename, interval_list):
    """read_fispact_out_dpa, read the dpa information of a cell
    include:dpa, and gas production"""
    # judge the interval_list
    if len(interval_list) != 0:
        errormessage = ''.join(['IRRADIATION_SCENARIO ERROR:\n',
                                '1. Only one pulse allowed, and it must be a FPY (1 year).\n',
                                '2. No cooling time allowed.'])
        raise ValueError(errormessage)
    # read the dpa information
    fin = open(filename)
    H_pro = 0.0
    He_pro = 0.0
    while True:
        line = fin.readline()
        line_ele = line.split()
        if line == '':  # end of the file, but not found the key word
            raise ValueError(
                'Total Displacement Rate (n,Dtot ) not found in the file, check')
        if 'Total Displacement Rate (n,Dtot )' in line:
            c.dpa = float(line_ele[-2])
        if 'APPM OF He  4' in line:
            He_pro += float(line_ele[-1])
        if 'APPM OF He  3' in line:
            He_pro += float(line_ele[-1])
        if 'APPM OF H   3' in line:
            H_pro += float(line_ele[-1])
        if 'APPM OF H   2' in line:
            H_pro += float(line_ele[-1])
        if 'APPM OF H   1' in line:
            H_pro += float(line_ele[-1])
        if 'COMPOSITION  OF  MATERIAL  BY  ELEMENT' in line:
            break
    fin.close()
    c.He_production = He_pro
    c.H_production = H_pro


def is_cooling_time_in_line(ct, line):
    """
    Check whether the cooling time (ct) in line.
    """
    if ('TIME INTERVAL' not in line) or ('COOLING TIME' not in line) or ('ELAPSED TIME' not in line):
        return False
    else:
        elapsed_time = get_elapsed_time_from_line(line)
        if math.isclose(elapsed_time, ct):
            return True
        else:
            return False


def get_elapsed_time_from_line(line):
    """
    Get the elapsed time (s) for a line contain 'ELAPSED TIME IS'.
    """
    ls = line.strip().split('*')
    ls = [i for i in ls if (i and i != ' ')]
    elapsed_time = ls[-1].strip().split('ELAPSED TIME IS')[-1].strip()
    elapsed_time = utils.time_to_sec(
        elapsed_time.split()[0], elapsed_time.split()[-1])
    return elapsed_time


def read_material_composition(filename, interval):
    """
    Read the material compositon in fispact output file.

    Parameters:
    -----------
    filename: str
        The output file name (including path).
    interval: int
        The interval number to read.

    Returns:
    --------
    mat: Material
        The material to be returned.
    """
    density = 0.0
    nucs = []
    nuc_atoms = []
    found_interval = False
    # read to interval specificed (is interval_in_line)
    with open(filename) as fin:
        while True:
            line = fin.readline()
            if line == '':
                errormessage = ''.join(['File: ', filename,
                                        ' does not have interval message, incomplete file!'])
                raise ValueError(errormessage)
            if is_interval_in_line(interval, line):
                found_interval = True
                line = fin.readline()  # unit
                line = fin.readline()  # empty blank
                # read atom name and atom numbers (per kg) line by line
                while True:
                    line = fin.readline()
                    if utils.is_blank_line(line):
                        continue
                    if ("TOTAL NUMBER OF NUCLIDES PRINTED" in line):
                        break
                    if line == '':
                        raise ValueError(
                            f"inventory information in {filename} interval {interval} unexpect end")
                    nuc, atoms, act, contact_dose, ci, hf_lf, dh = get_fispact_out_line_info(
                        line)
                    nucs.append(nuc)
                    nuc_atoms.append(atoms)
            if "DENSITY" in line and found_interval:
                line_ele = line.strip().split()
                density = float(line_ele[-2])
                break
    # return density, nucs and nuc_atoms
    return density, nucs, nuc_atoms


def get_material_after_irradiation(filename, mid=10001):
    """
    The the updated material compositon after irradiation. The material
    compostion after the last irradiation interval will be read for the
    creation of a new material.

    Parameters:
    -----------
    filename: str
        The FISPACT-II output file.
    mid: int
        The material id for the created material.

    Returns:
    --------
    mat: Material
        The created material with updated material composition.
    """
    interval_irrads = get_interval_list(filename, irradiation_only=True)
    density, nucs, nuc_atoms = read_material_composition(
        filename, interval_irrads[-1])
    mat = material.Material()
    mat.id = mid
    mat.density = density
    mat.fispact_material_nuclide = nucs
    mat.fispact_material_atom_kilogram = nuc_atoms
    return mat
