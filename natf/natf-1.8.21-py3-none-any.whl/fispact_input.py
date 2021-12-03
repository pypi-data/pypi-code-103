#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import re
import os
from natf import utils


def is_comment(line):
    """Check whether this line is a comment line for FISPACT input"""
    comment_pattern = re.compile("^<<.*>>", re.IGNORECASE)
    if re.match(comment_pattern, line):
        return True
    else:
        return False

# ========= IRRADIATION SCENARIO =========


def get_flux(line):
    """
    Get the power time from a line with FLUX.
    """
    # get power
    line_ele = line.strip().split()
    flux = float(line_ele[1])
    return flux


def get_power(line):
    """
    Get the power time from a line with FLUX.
    """
    # get power
    flux = get_flux(line)
    power = utils.neutron_intensity_to_power(flux)
    return power


def get_time(line, unit='s'):
    """
    Get the irradiation or cooling time from line.

    Parameters:
    -----------
    line: str
        The line to extract data.
    unit: str
        The output unit of time, default is [s].
    """
    line_ele = line.strip().split()
    time_s = utils.time_to_sec(line_ele[1], line_ele[2])
    time = utils.time_sec_to_unit(time_s, unit)
    return time


def get_total_power_time(irradiation_scenario):
    """
    Get the total power time [MW*year] for a given irradiation scenario.
    """
    total_power_time = 0.0
    fin = open(irradiation_scenario, 'r')
    while True:
        line = fin.readline()
        if line == '':
            fin.close()
            raise ValueError(
                f"{irradiation_scenario} does not have a end (keywork: ZERO) of irradiation phase")
        if is_comment(line):
            continue
        if 'FLUX' in line.upper():
            power = get_power(line)
        if 'TIME' in line.upper():
            time = get_time(line, unit='a')
            total_power_time += power*time
        if 'ZERO' in line.upper():
            break
    fin.close()
    return total_power_time


def concate_irradiation_block(block, flux_line, time_line):
    """
    Concate the irradiation block.

    Parameters:
    -----------
    block: str
        Current irradiation block.
    flux_line: str
        The line contain 'FLUX' information, with '\n'.
    time_line: str
        The line contain 'TIME' information, with '\n'.

    Returns:
    block: str
        Updated block
    """

    flux_line = flux_line.strip()
    time_line = time_line.strip()
    if 'ZERO' in block and 'ZERO' in time_line:
        return block
    if len(block) > 0:
        block = f"{block}\n{flux_line}\n{time_line}"
    else:
        block = f"{flux_line}\n{time_line}"
    return block


def get_cooling_block(irradiation_scenario):
    """
    Get the cooling block of the irradiation scenario.
    """
    cooling_block = ''
    with open(irradiation_scenario, 'r') as fin:
        while True:
            line = fin.readline()
            if line == '':
                break
            if 'ZERO' in line.upper():
                while True:
                    line = fin.readline()
                    if line == '':
                        break
                    if is_comment(line):
                        continue
                    if 'TIME' in line.upper():
                        cooling_block = f"{cooling_block}{line}"
    return cooling_block


def create_sub_irradiation_scenario(irradiation_scenario, step, start_point):
    """
    Generate a sub irradiation scenario contains irradiation of power_time_step
    start from the given start_point.
    For example, total power time step 200, step 20, start 100 will generate a
    irradiation scenario start at 100 [MW*year], and last for 20 [MW*year].

    Parameters:
    -----------
    irradiation_scenario: str
        The irradiation scenario file 
    step: float
        The power_time_step [MW*year]
    start_point: float
        The start power*time point of irradiation [MW*year]
    """

    otext = ''
    irrad_count = 0.0
    current_point = 0.0
    with open(irradiation_scenario, 'r') as fin:
        while True:
            line = fin.readline()
            if line == '':
                break
            if is_comment(line):
                continue
            if 'FLUX' in line.upper():
                line1 = line
                power = get_power(line1)
                line2 = fin.readline()
                if 'ZERO' in line2.upper():  # flux 0.0
                    otext = f"{otext}\n{line1}\n{line2}"
                    fin.close()
                    return otext
                time = get_time(line2, unit='a')
                irrad_count += power*time
                if irrad_count > start_point and irrad_count <= start_point + step:
                    # keep the remain time of current flux
                    tmp_time = (
                        irrad_count - max(current_point, start_point)) / power
                    tmp_line = f"TIME {tmp_time} YEARS ATOMS\n"
                    current_point += power*tmp_time
                    otext = concate_irradiation_block(otext, line1, tmp_line)
                    # check the next flux, if it's cooling, use it, otherwise ignore
                    last_pos = fin.tell()
                    while True:
                        next_line = fin.readline()
                        if is_comment(next_line):
                            continue
                        if 'FLUX' in next_line:
                            next_power = get_power(next_line)
                            if next_power <= 0:
                                next_time_line = fin.readline()
                                otext = concate_irradiation_block(
                                    otext, next_line, next_time_line)
                                if irrad_count == start_point + step:
                                    otext = concate_irradiation_block(
                                        otext, "FLUX 0.0", "ZERO")
                                    return otext
                            else:
                                # next flux is not zero, rewind to previous line
                                fin.seek(last_pos)
                            break
                elif irrad_count > start_point + step:
                    # flux do not change, but time change to step/power
                    tmp_time = (step - current_point) / power
                    if tmp_time > 0:
                        tmp_line = f"TIME {tmp_time} YEARS ATOMS\n"
                        otext = concate_irradiation_block(
                            otext, line1, tmp_line)
                    otext = concate_irradiation_block(
                        otext, "FLUX 0.0", "ZERO")
                    fin.close()
                    return otext
    fin.close()
    return otext


def split_irradiation_scenario(irradiation_scenario, power_time_step):
    """
    Split the irradiation scenario according to the power time step.
    General rules for splitting the irradiation scenario:
        - split only when power_time larger than step, otherwise raise an ValueError
        - if there are [n] sub-irradiation scenarios, the 1 to n-1 only irradiates, the last one irradiate then cooling
        - there may cooling between two irradiates, the cooling can not be used separately, put it in irradiates after cooling

    Parameters:
    -----------
    irradiation_scenario: str
        The irradiation scenario file
    power_time_step: float    
        The step in unit of [MW*year].

    Returns:
    --------
    irrad_scens: list of str
        The sub irradiation_scenario contents
    operation_times: list of float
        The operation time for each time step.
    """

    total_power_time = get_total_power_time(irradiation_scenario)
    sub_irrads = []
    operation_times = []
    fin = open(irradiation_scenario, 'r')
    if total_power_time <= power_time_step:
        text = fin.read()
        sub_irrads.append(text)
        fin.close()
        return sub_irrads, [total_power_time]
    else:
        current_point = 0.0
        remain_irrad = total_power_time
        while remain_irrad > 0:
            text = create_sub_irradiation_scenario(
                irradiation_scenario, power_time_step, current_point)
            sub_irrads.append(text)
            remain_irrad -= power_time_step
            current_point += power_time_step
            operation_times.append(min(current_point, total_power_time))

        # append the cooling block to the last irradiation scenario
        cooling_block = get_cooling_block(irradiation_scenario)
        sub_irrads[-1] = f"{sub_irrads[-1]}\n{cooling_block}"
        return sub_irrads, operation_times


def generate_sub_irradiation_files(irrad_blocks, dirname):
    """
    Generate sub-irradiation scenarios and put them info directories.

    Parameters:
    -----------
    irrad_blocks: list of str
        The sub-irradiation scenarios
    dirname: str
        The folder to store each sub irrads.
    """

    for i, irr in enumerate(irrad_blocks):
        subdir = os.path.join(dirname, f"step{i}")
        os.system(f"mkdir -pv {subdir}")
        ofname = os.path.join(subdir, "irradiation_scenario")
        with open(ofname, 'w') as fo:
            fo.write(irr+'\n')
