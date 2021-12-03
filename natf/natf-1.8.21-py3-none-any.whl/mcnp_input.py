#!/usr/bin/env python3
# -*- coding:utf-8 -*- import numpy as np import re
import argparse
import collections
import re
from natf import utils
from natf import cell

# patterns
comment_pattern = re.compile("^C ", re.IGNORECASE)
cont_pattern = re.compile("^      ")
comp_pattern = re.compile("^C *Component", re.IGNORECASE)
cell_range_pattern = re.compile("^C *Cell Range", re.IGNORECASE)
group_name_pattern = re.compile("^C *Group", re.IGNORECASE)
from_to_pattern = re.compile("^C.*From.*to", re.IGNORECASE)
new_comp_name_pattern = re.compile("^newcomp", re.IGNORECASE)
new_group_name_pattern = re.compile("^newgroup", re.IGNORECASE)
mat_title_pattern = re.compile("^M[1-9]", re.IGNORECASE)


def is_cell_title(line):
    """Check whether this line is the first line of a cell card"""
    line_ele = line.split()
    if len(line_ele) == 0:  # blank line
        return False
    # not surf title
    try:
        int(line_ele[1])
    except:
        return False
    # continue line
    if str(line_ele[0]).isdigit() and (not re.match(cont_pattern, line)):
        return True
    return False


def is_mat_title(line):
    """Check whether this line is the first line of a material card"""
    if re.match(mat_title_pattern, line):
        return True
    else:
        return False


def is_fn_tally_title(line):
    """
    Check whether this line is the title of Fn tally card.
    """
    fn_pattern = re.compile("^F[1-9]", re.IGNORECASE)
    if re.match(fn_pattern, line):
        return True
    else:
        return False


def is_fmeshn_tally_title(line):
    """
    Check whether this line is the title of FMESHn tally card.
    """
    fmeshn_pattern = re.compile("^FMESH[1-9]", re.IGNORECASE)
    if re.match(fmeshn_pattern, line):
        return True
    else:
        return False


def is_tally_title(line):
    """
    Check whether this line is the title of tally card
    """
    if is_fn_tally_title(line) or is_fmeshn_tally_title(line):
        return True
    else:
        return False


def get_cell_cid_mid_den(line):
    """Get the cell id, mid and density information"""
    line_ele = line.split()
    cid = int(line_ele[0])
    mid = int(line_ele[1])
    den = None
    if mid > 0:
        if '(' in line_ele[2]:
            tokens = line_ele[2].split('(')
            den = float(tokens[0])
        else:
            den = float(line_ele[2])
    elif mid == 0:
        pass
    else:
        raise ValueError(f"Wrong cell title line: {line}")
    return cid, mid, den


def cell_title_change_mat(cell_title, mid_new=0, den_new=0.0, atom_den_new=0.0):
    """Change the material in cell title"""
    line_ele = cell_title.split()
    cid = int(line_ele[0])
    mid = int(line_ele[1])
    rest = []
    if mid > 0:
        if '(' in line_ele[2]:
            tokens = line_ele[2].split('(')
            rest.append('('+tokens[1])
            rest.extend(line_ele[3:])
        else:
            rest.extend(line_ele[3:])
    elif mid == 0:
        rest.extend(line_ele[2:])
    else:
        raise ValueError(f"Wrong cell title line: {cell_title}")

    if mid_new == 0:
        return f"{cid} 0 {' '.join(rest)}"
    if mid_new > 0:
        if den_new > 0:
            return f"{cid} {mid_new} {-den_new} {' '.join(rest)}"
        elif atom_den_new > 0:
            return f"{cid} {mid_new} {atom_den_new} {' '.join(rest)}"
        else:
            raise ValueError(
                "Wrong den_new:{den_new} and atom_den_new:{atom_den_new}")
    raise ValueError("Wrong mid_new:{mid_new}")


def is_comment(line):
    """Check whether this line is a comment line"""
    if re.match(comment_pattern, line):
        return True
    else:
        return False


def has_comp_name(line):
    """Check whether this line contains component name"""
    if not is_comment(line):
        return False
    if re.match(comp_pattern, line):
        return True
    else:
        return False


def get_comp_name(line, new_comp_count=0):
    """Get the component name"""
    line_ele = line.split()
    if line_ele[-1].lower() == "component:":
        return f"newcomp{new_comp_count+1}"
    else:
        return line_ele[-1]


def has_cell_range(line):
    """Check whether this line contains cell range info"""
    if not is_comment(line):
        return False
    if re.match(cell_range_pattern, line):
        return True
    else:
        return False


def get_cell_range(line):
    """Get the cell range"""
    line_ele = line.split()
    cids = [range(int(line_ele[-3]), int(line_ele[-1]) + 1)]
    return cids


def has_group_name(line):
    """Check whether this line cntains group name"""
    if re.match(group_name_pattern, line):
        return True
    else:
        return False


def get_group_name(line, new_group_count=0):
    line_ele = line.split()
    if line_ele[-1].lower() == "group:":
        return f"newcomp{new_group_count+1}"
    else:
        return line_ele[-1]


def has_from_to(line):
    if re.match(from_to_pattern, line):
        return True
    else:
        return False


def get_nonvoid_cells(inp="input"):
    """
    Read the MCNP input file generated by cosVMPT and output a list of all
    non-void cells"
    """
    nonvoid_cells = []
    with open(inp, 'r') as fin:
        cell_card_end = False
        while not cell_card_end:
            line = fin.readline()
            if utils.is_blank_line(line):  # end of cell card
                cell_card_end = True
                break
            if is_cell_title(line):
                line_ele = line.split()
                mid = int(line_ele[1])
                if mid > 0:
                    nonvoid_cells.append(int(line_ele[0]))
    return nonvoid_cells


def mcnp_tally_style(cids, sds=None, output="tally_card.txt"):
    """Convert the cell number list to a mcnp style tally description."""
    tally_card = f'C tallied cell numbers: {len(cids)}'
    tally_card = f'{tally_card}\nFC4 tally card generated via natf:mcnp_tally_style'
    tally_card = f'{tally_card}\nF4:n  '
    for i, cid in enumerate(cids):
        tally_card = utils.mcnp_style_str_append(tally_card, str(cid))
    if sds is not None:
        tally_card = f"{tally_card}\nSD4   "
        for i, sd in enumerate(sds):
            tally_card = utils.mcnp_style_str_append(tally_card, str(sd))
    with open(output, 'w') as fo:
        fo.write(tally_card+'\n')


def cell_vol_err_reader(inp="input"):
    """Read the cell-vol-err info file"""
    cids, vols, errs = [], [], []
    # Opening file and read data
    fin = open(inp, 'r')
    for line in fin:
        if utils.is_blank_line(line):
            break
        line_ele = line.split()
        cids.append(int(line_ele[0]))
        vols.append(float(line_ele[1]))
        errs.append(float(line_ele[2]))
    fin.close()
    return cids, vols, errs


def cell_vol_to_tally(inp="input", output="tally_card.txt"):
    """
    Write the cell, vol, err info to tally card.
    """
    cell_vol_to_tally_help = ('This script read a cell-vol-err info file and\n'
                              'return a tally style string.\n')

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=False,
                        help="cell-vol-err in file path")
    parser.add_argument("-o", "--output", required=False,
                        help="save the tally_card to output file")
    args = vars(parser.parse_args())

    input_file = "input"
    if args['input'] is not None:
        input_file = args['input']
    cids, vols, errs = cell_vol_err_reader(input_file)
    # save data into a tally style card
    output = "tally_card.txt"
    if args['output'] is not None:
        output = args['output']
    mcnp_tally_style(cids, sds=vols, output=output)


def nonvoid_cells_to_tally():
    nonvoid_cells_help = ('This script read a mcnp input file and return a tally style\n'
                          'string of all non-void cells.\n')
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=False,
                        help="mcnp input file path")
    parser.add_argument("-o", "--output", required=False,
                        help="save the string to output file")
    args = vars(parser.parse_args())

    input_file = "input"
    if args['input'] is not None:
        input_file = args['input']
    nonvoid_cells = get_nonvoid_cells(input_file)

    output = "output.txt"
    if args['output'] is not None:
        output = args['output']
    mcnp_tally_style(nonvoid_cells, output=output)


def get_part_cell_list(inp):
    """Read the components and groups input file generated by cosVMPT."""
    parts = collections.OrderedDict()
    # comps = collections.OrderedDict()  # {'name':[{group1:cids}, {group2:cids}, ...]}
    # group = collections.OrderedDict() # {'name':[cids]}
    current_comp, current_group, current_cell = None, None, None
    new_comp_count, new_group_count = 0, 0

    # read the file
    with open(inp, 'r') as fin:
        cell_card_end = False
        while not cell_card_end:
            line = fin.readline()
            if utils.is_blank_line(line):  # end of cell card
                cell_card_end = True
                break
            if has_comp_name(line):
                current_comp = get_comp_name(
                    line, new_comp_count=new_comp_count)
                if re.match(new_comp_name_pattern, current_comp):
                    new_comp_count += 1
                #comps[current_comp] = []
                parts[current_comp] = []
                continue
            if has_group_name(line):
                current_group = get_group_name(line, new_group_count)
                if re.match(new_group_name_pattern, current_group):
                    new_group_count += 1
                #group[current_group] = []
                current_part = f"{current_comp}-{current_group}"
                parts[current_part] = []
                #comps[current_comp][current_group] = []
                continue
            if is_cell_title(line):
                line_ele = line.split()
                mid = int(line_ele[1])
                if mid > 0:  # nonvoid cell
                    #    comps[current_comp].append(int(line_ele[0]))
                    parts[current_comp].append(int(line_ele[0]))
                    parts[current_part].append(int(line_ele[0]))
    return parts


def format_cell_list(name, cids):
    """Format the cell list to part_cell_list style"""
    cnt = name
    for i, cid in enumerate(cids):
        cnt = utils.mcnp_style_str_append(cnt, str(cid))
    return cnt


def save_part_cell_list(parts, output):
    """Write the components and groups cells in format of part_cell_list"""
    cnt = f"C Be careful about the content, do not enter any characters except ASCII."
    cnt = f"{cnt}\nC Lines start with `C ` is comment"
    cnt = f"{cnt}\nC Syntax of defing parts: part_name cell_list"
    cnt = f"{cnt}\nC Refer to 'NATF manual` for more details about defining parts."
    cnt = f"{cnt}\nC Generated by natf:part_cell_list"
    for key, value in parts.items():
        if len(value) > 0:  # void, do not print
            cnt = f"{cnt}\n{format_cell_list(key, value)}"
    with open(output, 'w') as fo:
        fo.write(cnt)


def part_cell_list(inp="input", output="part_cell_list.txt"):
    """
    Read the components and groups input file generated by cosVMPT, and
    write a part_cell_list file for NATF.
    """
    list_comp_group_help = ('This script read a mcnp input file and return a\n'
                            'part_cell_list file.\n')
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=False,
                        help="mcnp input file path, default: input")
    parser.add_argument("-o", "--output", required=False,
                        help="name of the part_cell_list file, default: part_cell_list.txt")
    args = vars(parser.parse_args())

    # read the file
    if args['input'] is not None:
        inp = args['input']
    parts = get_part_cell_list(inp)

    # save the content
    if args['output'] is not None:
        output = args['output']
    save_part_cell_list(parts, output=output)


def update_mcnp_input_materials(filename, cells, ofname):
    """
    Update the materials of the mcnp input file.
    """
    fo = open(ofname, 'w')
    mat_written = False
    with open(filename, 'r') as fin:
        while True:
            line = fin.readline()
            if line == '':
                break
            if is_cell_title(line):
                # get the cell id
                cid, mid, den = get_cell_cid_mid_den(line)
                # whether in cells
                if cell.is_item_cell(cid, cells):
                    cidx = cell.get_cell_index(cells, cid)
                    # get info of new material
                    mid_new = cells[cidx].mid
                    # replace with new material
                    new_line = cell_title_change_mat(
                        line, mid_new, atom_den_new=cells[cidx].mat.atom_density)
                    fo.write(new_line+"\n")
                    continue
            if is_mat_title(line) and not mat_written:
                # write all new materials before previous materials
                for c in cells:
                    fo.write(c.mat.__str__()+"\n")
                mat_written = True
                # write the original materials and the rest contents
                fo.write(line)
                while True:
                    line = fin.readline()
                    if line == '':
                        return
                    fo.write(line)
            # other lines
            fo.write(line)


def get_tally_id(line):
    """
    Get the tally number (int) from tally title.
    """
    tokens = line.strip().split()
    item = tokens[0].split(":")[0]
    if is_fn_tally_title(line):
        tid = item[1:]
    else:
        tid = item[5:]
    return int(tid)


def get_tally_numbers(filename):
    """
    Get all the used tally numbers.
    """
    tally_nums = []
    with open(filename, 'r') as fin:
        while True:
            line = fin.readline()
            if line == '':
                break
            if is_tally_title(line):
                # get the cell id
                tid = get_tally_id(line)
                tally_nums.append(tid)
    return tally_nums


def calc_next_tid(tid, postfix=4):
    """
    Calculate the next available tally id for different type.
    """
    last_digit = tid % 10
    if last_digit < postfix:
        tid = (tid//10) * 10 + postfix
    else:
        tid = (tid//10 + 1) * 10 + postfix
    return tid


def compose_fn_tally_single(tid, cid, mid=None, particle='N', sd=1.0, mt=None):
    """
    Compose a tally string. 
    """
    s = f"F{tid}:{particle} {cid}"
    if mid is not None and mt is not None:
        s = f"{s}\nFM{tid} -1 {mid} {mt}"
    s = f"{s}\nSD{tid} {sd}\n"
    #s = f"{s}\nFQ{tid} f e\n"
    return s


def update_mcnp_input_tallies(filename, cells, tid_start=10000, write_file=True):
    """
    Update the tallies of the mcnp input file.
    The TBR for cells will be added to tallies.
    """
    current_tid = tid_start
    new_tallies = []
    fo = open(filename, 'a')
    for i, cell in enumerate(cells):
        current_tid = calc_next_tid(current_tid)
        new_tallies.append(current_tid)
        tally_string = compose_fn_tally_single(
            tid=current_tid, cid=cell.id, mid=cell.mid, mt=205)
        if write_file:
            fo.write(tally_string)
    fo.close()
    return new_tallies
