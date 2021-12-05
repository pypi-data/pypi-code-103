##
# File: CifReader.py derived from wwpdb.apps.ccmodule.io.ChemCompIo.py
# Date: 31-May-2010  John Westbrook
#
# Update:
# 06-Aug-2010 - jdw - Generalized construction of methods to apply to any category
#                     Add accessors for lists of dictionaries.
# 12-May-2011 - rps - Added check for None when asking for category Object in __getDataList()
# 2012-10-24    RPS   Updated to reflect reorganization of modules in pdbx packages
# 23-Jul-2019   my  - forked original code to wwpdb.util.nmr.CifReader
# 30-Jul-2019   my  - add 'range-float' as filter item type
# 05-Aug-2019   my  - add 'enum' as filter item type
# 28-Jan-2020   my  - add 'withStructConf' option of getPolymerSequence
# 19-Mar-2020   my  - add hasItem()
# 24-Mar-2020   my  - add 'identical_chain_id' in results of getPolymerSequence()
# 15-Apr-2020   my  - add 'total_models' option of getPolymerSequence (DAOTHER-4060)
# 19-Apr-2020   my  - add random rotation test for detection of non-superimposed models (DAOTHER-4060)
# 08-May-2020   my  - make sure parse() is run only once (DAOTHER-5654)
# 20-Nov-2020   my  - additional support for insertion code in getPolymerSequence() (DAOTHER-6128)
# 29-Jun-2021   my  - add 'auth_chain_id', 'identical_auth_chain_id' in results of getPolymerSequence() if possible (DAOTHER-7108)
##
""" A collection of classes for parsing CIF files.
"""

import sys
import os
import traceback
import math
from mmcif.io.PdbxReader import PdbxReader

import numpy as np

import random


def to_np_array(a):
    """ Return Numpy array of a given Cartesian coordinate in {'x': float, 'y': float, 'z': float} format.
    """

    return np.asarray([a['x'], a['y'], a['z']])


def M(axis, theta):
    """ Return the rotation matrix associated with counterclockwise rotation about the given axis by theta radians.
    """

    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d

    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


class CifReader(object):
    """ Accessor methods for parsing CIF files.
    """
    def __init__(self, verbose=True, log=sys.stdout):
        self.__verbose = verbose
        self.__lfh = log

        # file path
        self.__filePath = None

        # active data block
        self.__dBlock = None

        # preset values
        self.emptyValue = (None, '', '.', '?')
        self.trueValue = ('true', 't', 'yes', 'y', '1')

        # allowed item types
        self.itemTypes = ('str', 'bool', 'int', 'float', 'range-float', 'enum')

        # whether to hold RMSD calculation details
        self.__hold_rmsd_calculation = False

        # random rotation test for detection of non-superimposed models (DAOTHER-4060)
        self.__random_rotaion_test = False
        self.__single_model_rotation_test = True

        if self.__random_rotaion_test:
            self.__lfh.write("+WARNING- CifReader.__init__() Enabled random rotation test\n")
            self.__lfh.write("+WARNING- CifReader.__init__() Single model rotation test: %s\n" % self.__single_model_rotation_test)

    def parse(self, filePath):
        """ Set file path and parse CIF file, and set internal active data block if possible.
            @return: True for success or False otherwise.
        """

        if self.__dBlock is not None and self.__filePath == filePath:
            return True

        self.__dBlock = None
        self.__filePath = filePath

        try:
            if not os.access(self.__filePath, os.R_OK):
                if self.__verbose:
                    self.__lfh.write("+ERROR- CifReader.setFilePath() Missing file %s\n" % self.__filePath)
                return False
            return self.__parse()
        except:  # noqa: E722 pylint: disable=bare-except
            if self.__verbose:
                self.__lfh.write("+ERROR- CifReader.setFilePath() Missing file %s\n" % self.__filePath)
            return False

    def __parse(self):
        """ Parse CIF file and set internal active data block.
            @return: True for success or False otherwise.
        """

        if self.__dBlock is not None:
            return True

        try:
            block = self.__getDataBlock()
            return self.__setDataBlock(block)
        except:  # noqa: E722 pylint: disable=bare-except
            traceback.print_exc(file=sys.stdout)
            return False

    def __getDataBlock(self, blockId=None):
        """ Worker method to read cif file and set the target datablock
            If no blockId is provided return the first data block.
            @return: target data block
        """

        with open(self.__filePath, 'r') as ifh:
            myBlockList = []
            pRd = PdbxReader(ifh)
            pRd.read(myBlockList)
            if blockId is not None:
                for block in myBlockList:
                    if block.getType() == 'data' and block.getName() == blockId:
                        return block
            else:
                for block in myBlockList:
                    if block.getType() == 'data':
                        return block

            return None

    def __setDataBlock(self, dataBlock=None):
        """ Assigns the input data block as the active internal data block.
            @return: True for success or False otherwise.
        """

        ok = False

        try:
            if dataBlock.getType() == 'data':
                self.__dBlock = dataBlock
                ok = True
            else:
                self.__dBlock = None
        except:  # noqa: E722 pylint: disable=bare-except
            pass

        return ok

    def hasCategory(self, catName):
        """ Return whether a given category exists.
        """

        if self.__dBlock is None:
            return False

        return catName in self.__dBlock.getObjNameList()

    def hasItem(self, catName, itName):
        """ Return whether a given item exists in a category.
        """

        if self.__dBlock is None:
            return False

        # get category object
        catObj = self.__dBlock.getObj(catName)

        if catObj is None:
            return False

        len_catName = len(catName) + 2

        return itName in [j[len_catName:] for j in catObj.getItemNameList()]

    def getDictList(self, catName):
        """ Return a list of dictionaries of a given category.
        """

        dList = []

        if self.__dBlock is None:
            return dList

        # get category object
        catObj = self.__dBlock.getObj(catName)

        if catObj is not None:
            len_catName = len(catName) + 2

            # get column name index
            itDict = {}
            itNameList = catObj.getItemNameList()
            for idxIt, itName in enumerate(itNameList):
                itDict[itName[len_catName:]] = idxIt

            # get row list
            rowList = catObj.getRowList()

            for row in rowList:
                tD = {}
                for k, v in itDict.items():
                    tD[k] = row[v]
                dList.append(tD)

        return dList

    def getPolymerSequence(self, catName, keyItems, withStructConf=False, alias=False, total_models=1):
        """ Extracts sequence from a given loop in a CIF file
        """

        keyNames = [k['name'] for k in keyItems]

        len_key = len(keyItems)

        asm = []  # assembly of a loop

        if self.__dBlock is None:
            return asm

        # get category object
        catObj = self.__dBlock.getObj(catName)

        if catObj is not None:
            len_catName = len(catName) + 2

            # get column name index
            itDict = {}
            altDict = {}

            itNameList = [j[len_catName:] for j in catObj.getItemNameList()]

            for idxIt, itName in enumerate(itNameList):
                itDict[itName] = idxIt
                if itName in keyNames:
                    altDict[next(k['alt_name'] for k in keyItems if k['name'] == itName)] = idxIt

            if set(keyNames) & set(itDict.keys()) != set(keyNames):
                raise LookupError("Missing one of data items %s." % keyNames)

            # get row list
            rowList = catObj.getRowList()

            for row in rowList:
                for j in range(len_key):
                    itCol = itDict[keyNames[j]]
                    if itCol < len(row) and row[itCol] in self.emptyValue:
                        if 'default' not in keyItems[j] and keyItems[j]['default'] not in self.emptyValue:
                            raise ValueError("%s must not be empty." % keyNames[j])

            compDict = {}
            seqDict = {}
            insCodeDict = {}
            labelSeqDict = {}

            authChainDict = {}

            chain_id_col = altDict['chain_id']
            seq_id_col = altDict['seq_id']
            comp_id_col = altDict['comp_id']
            ins_code_col = -1 if 'ins_code' not in altDict else altDict['ins_code']
            label_seq_col = -1 if 'label_seq_id' not in altDict else altDict['label_seq_id']
            auth_chain_id_col = -1 if 'auth_chain_id' not in altDict else altDict['auth_chain_id']

            chains = sorted(set([row[chain_id_col] for row in rowList]))

            if ins_code_col == -1 or label_seq_col == -1:
                sortedSeq = sorted(set(['{} {:04d} {}'.format(row[chain_id_col], int(row[seq_id_col]), row[comp_id_col]) for row in rowList]))

                keyDict = {'{} {:04d}'.format(row[chain_id_col], int(row[seq_id_col])): row[comp_id_col] for row in rowList}

                for row in rowList:
                    key = '{} {:04d}'.format(row[chain_id_col], int(row[seq_id_col]))
                    if keyDict[key] != row[comp_id_col]:
                        raise KeyError("Sequence must be unique. %s %s, %s %s, %s %s vs %s." %
                                       (itNameList[chain_id_col], row[chain_id_col],
                                        itNameList[seq_id_col], row[seq_id_col],
                                        itNameList[comp_id_col], row[comp_id_col], keyDict[key]))

                if len(chains) > 1:
                    for c in chains:
                        compDict[c] = [s.split(' ')[-1] for s in sortedSeq if s.split(' ')[0] == c]
                        seqDict[c] = [int(s.split(' ')[1]) for s in sortedSeq if s.split(' ')[0] == c]
                else:
                    c = list(chains)[0]
                    compDict[c] = [s.split(' ')[-1] for s in sortedSeq]
                    seqDict[c] = [int(s.split(' ')[1]) for s in sortedSeq]

            else:
                sortedSeq = sorted(set(['{} {:04d} {} {} {}'.format(row[chain_id_col], int(row[seq_id_col]), row[ins_code_col], row[label_seq_col], row[comp_id_col]) for row in rowList]))

                keyDict = {'{} {:04d} {} {}'.format(row[chain_id_col], int(row[seq_id_col]), row[ins_code_col], row[label_seq_col]): row[comp_id_col] for row in rowList}

                for row in rowList:
                    key = '{} {:04d} {} {}'.format(row[chain_id_col], int(row[seq_id_col]), row[ins_code_col], row[label_seq_col])
                    if keyDict[key] != row[comp_id_col]:
                        raise KeyError("Sequence must be unique. %s %s, %s %s, %s %s, %s %s, %s %s vs %s." %
                                       (itNameList[chain_id_col], row[chain_id_col],
                                        itNameList[seq_id_col], row[seq_id_col],
                                        itNameList[ins_code_col], row[ins_code_col],
                                        itNameList[label_seq_col], row[label_seq_col],
                                        itNameList[comp_id_col], row[comp_id_col], keyDict[key]))

                if len(chains) > 1:
                    for c in chains:
                        compDict[c] = [s.split(' ')[-1] for s in sortedSeq if s.split(' ')[0] == c]
                        seqDict[c] = [int(s.split(' ')[1]) for s in sortedSeq if s.split(' ')[0] == c]
                        insCodeDict[c] = [s.split(' ')[2] for s in sortedSeq if s.split(' ')[0] == c]
                        labelSeqDict[c] = [s.split(' ')[3] for s in sortedSeq if s.split(' ')[0] == c]
                else:
                    c = list(chains)[0]
                    compDict[c] = [s.split(' ')[-1] for s in sortedSeq]
                    seqDict[c] = [int(s.split(' ')[1]) for s in sortedSeq]
                    insCodeDict[c] = [s.split(' ')[2] for s in sortedSeq]
                    labelSeqDict[c] = [s.split(' ')[3] for s in sortedSeq]

            if auth_chain_id_col != -1:
                for row in rowList:
                    c = row[chain_id_col]
                    if c not in authChainDict:
                        authChainDict[c] = row[auth_chain_id_col]

            asm = []  # assembly of a loop

            for c in chains:
                ent = {}  # entity

                ent['chain_id'] = c
                ent['seq_id'] = seqDict[c]
                ent['comp_id'] = compDict[c]
                if c in insCodeDict and any(s not in self.emptyValue for s in labelSeqDict[c]):
                    ent['ins_code'] = insCodeDict[c]
                    if c in labelSeqDict and all(s.isdigit() for s in labelSeqDict[c]):
                        ent['auth_seq_id'] = seqDict[c]
                        ent['label_seq_id'] = [int(s) for s in labelSeqDict[c]]
                        ent['seq_id'] = ent['label_seq_id']

                if auth_chain_id_col != -1:
                    ent['auth_chain_id'] = authChainDict[c]

                if withStructConf:
                    ent['struct_conf'] = self.__extractStructConf(c, seqDict[c], alias)

                entity_poly = self.getDictList('entity_poly')

                etype = next((e['type'] for e in entity_poly if 'pdbx_strand_id' in e and c in e['pdbx_strand_id'].split(',')), None)

                if etype is not None:
                    ent['type'] = etype

                    if total_models > 1:

                        randomM = None
                        if self.__random_rotaion_test:
                            randomM = {}
                            for model_id in range(1, total_models + 1):
                                axis = [random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)]
                                if self.__single_model_rotation_test:
                                    theta = 0.0 if model_id > 1 else np.pi / 4.0
                                else:
                                    theta = random.uniform(-np.pi, np.pi)
                                randomM[model_id] = M(axis, theta)

                        if 'polypeptide' in etype:

                            ca_atom_sites = self.getDictListWithFilter('atom_site',
                                                                       [{'name': 'Cartn_x', 'type': 'float', 'alt_name': 'x'},
                                                                        {'name': 'Cartn_y', 'type': 'float', 'alt_name': 'y'},
                                                                        {'name': 'Cartn_z', 'type': 'float', 'alt_name': 'z'},
                                                                        {'name': 'label_seq_id', 'type': 'int', 'alt_name': 'seq_id'},
                                                                        {'name': 'ndb_model' if alias else 'pdbx_PDB_model_num', 'type': 'int', 'alt_name': 'model_id'}
                                                                        ],
                                                                       [{'name': 'label_asym_id', 'type': 'str', 'value': c},
                                                                        {'name': 'label_atom_id', 'type': 'str', 'value': 'CA'}])

                            ent['ca_rmsd'] = self.__calculateRMSD(c, seqDict[c], alias, total_models, ca_atom_sites, randomM)

                        elif 'ribonucleotide' in etype:

                            p_atom_sites = self.getDictListWithFilter('atom_site',
                                                                      [{'name': 'Cartn_x', 'type': 'float', 'alt_name': 'x'},
                                                                       {'name': 'Cartn_y', 'type': 'float', 'alt_name': 'y'},
                                                                       {'name': 'Cartn_z', 'type': 'float', 'alt_name': 'z'},
                                                                       {'name': 'label_seq_id', 'type': 'int', 'alt_name': 'seq_id'},
                                                                       {'name': 'ndb_model' if alias else 'pdbx_PDB_model_num', 'type': 'int', 'alt_name': 'model_id'}
                                                                       ],
                                                                      [{'name': 'label_asym_id', 'type': 'str', 'value': c},
                                                                       {'name': 'label_atom_id', 'type': 'str', 'value': 'P'}])

                            ent['p_rmsd'] = self.__calculateRMSD(c, seqDict[c], alias, total_models, p_atom_sites, randomM)

                if len(chains) > 1:
                    identity = []
                    for _c in chains:
                        if _c == c:
                            continue
                        if compDict[_c] == compDict[c]:
                            identity.append(_c)
                    if len(identity) > 0:
                        ent['identical_chain_id'] = identity
                        if auth_chain_id_col != -1:
                            ent['identical_auth_chain_id'] = [authChainDict[c] for c in identity]

                asm.append(ent)

        return asm

    def __extractStructConf(self, chain_id, seq_ids, alias=False):
        """ Extract structure conformational annotations.
        """

        ret = [None] * len(seq_ids)

        struct_conf = self.getDictListWithFilter('struct_conf',
                                                 [{'name': 'conf_type_id', 'type': 'str'},
                                                  {'name': 'pdb_id' if alias else 'pdbx_PDB_helix_id', 'type': 'str', 'alt_name': 'helix_id'},
                                                  {'name': 'beg_label_seq_id', 'type': 'int'},
                                                  {'name': 'end_label_seq_id', 'type': 'int'}
                                                  ],
                                                 [{'name': 'beg_label_asym_id', 'type': 'str', 'value': chain_id},
                                                  {'name': 'end_label_asym_id', 'type': 'str', 'value': chain_id}
                                                  ])

        for sc in struct_conf:
            for seq_id in range(sc['beg_label_seq_id'], sc['end_label_seq_id'] + 1):
                if seq_id in seq_ids and not sc['conf_type_id'] is None and not sc['helix_id'] is None:
                    ret[seq_ids.index(seq_id)] = sc['conf_type_id'] + ':' + sc['helix_id']

        struct_sheet_range = self.getDictListWithFilter('struct_sheet_range',
                                                        [{'name': 'sheet_id', 'type': 'str'},
                                                         {'name': 'id', 'type': 'str'},
                                                         {'name': 'beg_label_seq_id', 'type': 'int'},
                                                         {'name': 'end_label_seq_id', 'type': 'int'}
                                                         ],
                                                        [{'name': 'beg_label_asym_id', 'type': 'str', 'value': chain_id},
                                                         {'name': 'end_label_asym_id', 'type': 'str', 'value': chain_id}
                                                         ])

        for ssr in struct_sheet_range:
            for seq_id in range(ssr['beg_label_seq_id'], ssr['end_label_seq_id'] + 1):
                if seq_id in seq_ids and not ssr['sheet_id'] is None and not ssr['id'] is None:
                    ret[seq_ids.index(seq_id)] = 'STRN:' + ssr['sheet_id'] + ':' + ssr['id']

        return ret

    def __calculateRMSD(self, chain_id, seq_ids, alias=False, total_models=1, atom_sites=None, randomM=None):  # pylint: disable=unused-argument
        """ Calculate RMSD of alpha carbons/phosphates in the ensemble.
        """

        rlist = []

        for ref_model_id in range(1, total_models + 1):

            item = {'model_id': ref_model_id}

            ret = [None] * len(seq_ids)

            if total_models > 1 and atom_sites is not None:

                for seq_id in seq_ids:

                    _atom_site = [a for a in atom_sites if a['seq_id'] == seq_id]

                    if len(_atom_site) == total_models:
                        try:
                            ref_atom = next(ref_atom for ref_atom in _atom_site if ref_atom['model_id'] == ref_model_id)
                            ref_v = to_np_array(ref_atom)
                            if self.__random_rotaion_test:
                                ref_v = np.dot(randomM[ref_model_id], ref_v)
                            rmsd2 = 0.0
                            for atom in [atom for atom in _atom_site if atom['model_id'] != ref_model_id]:
                                v = to_np_array(atom)
                                if self.__random_rotaion_test:
                                    v = np.dot(randomM[atom['model_id']], v)
                                d = v - ref_v
                                rmsd2 += np.dot(d, d)
                        except StopIteration:
                            continue

                        ret[seq_ids.index(seq_id)] = float('{:.2f}'.format(math.sqrt(rmsd2 / (total_models - 1))))

            if self.__hold_rmsd_calculation:
                item['rmsd'] = ret

            _ret = [r for r in ret if r is not None]

            _len_rmsd = len(_ret)

            if _len_rmsd >= 8:
                _mean_rmsd = sum(_ret) / _len_rmsd
                _stddev_rmsd = math.sqrt(sum([(r - _mean_rmsd) ** 2 for r in _ret]) / (_len_rmsd - 1))

                item['filtered_total_count'] = [_len_rmsd]
                item['filtered_mean_rmsd'] = [float('{:.2f}'.format(_mean_rmsd))]
                item['filtered_max_rmsd'] = [max(_ret)]
                item['filtered_stddev_rmsd'] = [float('{:.2f}'.format(_stddev_rmsd))]

                self.__calculateFilteredRMSD(_ret, _mean_rmsd, _stddev_rmsd, item)

            if not self.__hold_rmsd_calculation and 'filtered_total_count' in item:
                del item['filtered_total_count']
                del item['filtered_mean_rmsd']
                del item['filtered_max_rmsd']
                del item['filtered_stddev_rmsd']

            if 'rmsd_in_well_defined_region' in item:
                rlist.append(item)

        return rlist

    def __calculateFilteredRMSD(self, ret, mean_rmsd, stddev_rmsd, item):
        """ Calculate filtered RMSD.
        """

        _ret = [r for r in ret if r < mean_rmsd + stddev_rmsd]

        _len_rmsd = len(_ret)

        if _len_rmsd >= 8:
            _mean_rmsd = sum(_ret) / _len_rmsd
            _stddev_rmsd = math.sqrt(sum([(r - _mean_rmsd) ** 2 for r in _ret]) / (_len_rmsd - 1))

            item['filtered_total_count'].append(_len_rmsd)
            item['filtered_mean_rmsd'].append(float('{:.2f}'.format(_mean_rmsd)))
            item['filtered_max_rmsd'].append(max(_ret))
            item['filtered_stddev_rmsd'].append(float('{:.2f}'.format(_stddev_rmsd)))

            if mean_rmsd - _mean_rmsd > 0.2 or stddev_rmsd - _stddev_rmsd > 0.2:
                self.__calculateFilteredRMSD(_ret, _mean_rmsd, _stddev_rmsd, item)
            elif len(item['filtered_stddev_rmsd']) > 2:
                model = np.polyfit(item['filtered_stddev_rmsd'], item['filtered_mean_rmsd'], 2)
                for y in [1.0]:
                    item['rmsd_in_well_defined_region'] = float('{:.2f}'.format(model[2] + model[1] * y + model[0] * (y ** 2)))

    def getDictListWithFilter(self, catName, dataItems, filterItems=None):
        """ Return a list of dictionaries of a given category with filter.
        """

        dataNames = [d['name'] for d in dataItems]

        for d in dataItems:
            if not d['type'] in self.itemTypes:
                raise TypeError("Type %s of data item %s must be one of %s." % (d['type'], d['name'], self.itemTypes))

        if filterItems is not None:
            filterNames = [f['name'] for f in filterItems]

            for f in filterItems:
                if not f['type'] in self.itemTypes:
                    raise TypeError("Type %s of filter item %s must be one of %s." % (f['type'], f['name'], self.itemTypes))

        dList = []

        if self.__dBlock is None:
            return dList

        # get category object
        catObj = self.__dBlock.getObj(catName)

        if catObj is not None:
            len_catName = len(catName) + 2

            # get column name index
            colDict = {}
            fcolDict = {}

            itNameList = [j[len_catName:] for j in catObj.getItemNameList()]

            for idxIt, itName in enumerate(itNameList):
                if itName in dataNames:
                    colDict[itName] = idxIt
                if filterItems is not None and itName in filterNames:
                    fcolDict[itName] = idxIt

            if set(dataNames) & set(itNameList) != set(dataNames):
                raise LookupError("Missing one of data items %s." % dataNames)

            if filterItems is not None and set(filterNames) & set(itNameList) != set(filterNames):
                raise LookupError("Missing one of filter items %s." % filterNames)

            # get row list
            rowList = catObj.getRowList()

            for row in rowList:
                keep = True
                if filterItems is not None:
                    for filterItem in filterItems:
                        val = row[fcolDict[filterItem['name']]]
                        if val in self.emptyValue:
                            if not filterItem['value'] in self.emptyValue:
                                keep = False
                                break
                        else:
                            filterItemType = filterItem['type']
                            if filterItemType == 'str' or filterItemType == 'enum':
                                pass
                            elif filterItemType == 'bool':
                                val = val.lower() in self.trueValue
                            elif filterItemType == 'int':
                                val = int(val)
                            else:
                                val = float(val)
                            if filterItemType == 'range-float':
                                _range = filterItem['range']
                                if ('min_exclusive' in _range and val <= _range['min_exclusive']) or ('min_inclusive' in _range and val < _range['min_inclusive']) or ('max_inclusive' in _range and val > _range['max_inclusive']) or ('max_exclusive' in _range and val >= _range['max_exclusive']):  # noqa: E501
                                    keep = False
                                    break
                            elif filterItemType == 'enum':
                                if val not in filterItem['enum']:
                                    keep = False
                                    break
                            else:
                                if val != filterItem['value']:
                                    keep = False
                                    break

                if keep:
                    tD = {}
                    for dataItem in dataItems:
                        val = row[colDict[dataItem['name']]]
                        if val in self.emptyValue:
                            val = None
                        dataItemType = dataItem['type']
                        if dataItemType == 'str' or dataItemType == 'enum':
                            pass
                        elif dataItemType == 'bool':
                            val = val.lower() in self.trueValue
                        elif dataItemType == 'int' and val is not None:
                            val = int(val)
                        elif val is not None:
                            val = float(val)
                        if 'alt_name' in dataItem:
                            tD[dataItem['alt_name']] = val
                        else:
                            tD[dataItem['name']] = val
                    dList.append(tD)

        return dList
