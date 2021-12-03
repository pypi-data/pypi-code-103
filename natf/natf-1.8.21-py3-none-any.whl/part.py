#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import numpy as np
from natf.cell import Cell
from natf.radwaste_standard import RadwasteStandard
from natf import utils

gamma_energy_upper_bounds = [0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.40, 0.60,
                             0.80, 1.00, 1.22, 1.44, 1.66, 2.00, 2.50, 3.00,
                             4.00, 5.00, 6.50, 8.00, 10.00, 12.00, 14.00, 20.00]


class Part(object):
    '''class Part'''

    def __init__(self, name=''):
        self._name = name  # name of the part
        self._dirname = None  # directory for output files
        self._cell_ids = []  # list of cell ids
        self._subpart_ids = []
        self._part_cell_list = []  # a lis of Cell
        self._part_subpart_list = []  # list of sub parts
        self._mass_flow_rate = 0.0  # mass flot rate of this part
        self._node_part_count = []  # number of BLK modules merge into this node

    def __str__(self):
        p_str = f"Part name: {self.name}"
        p_str = f"{p_str}\npart_cell_list:"
        for c in self.part_cell_list:
            p_str = f"{p_str} {c.id}"
        return p_str

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError('name of the part must be string')
        self._name = value

    @property
    def dirname(self):
        return self._dirname

    @dirname.setter
    def dirname(self, value):
        if not isinstance(value, str):
            raise ValueError('dirname of the part must be string')
        self._dirname = value

    @property
    def cell_ids(self):
        return self._cell_ids

    @cell_ids.setter
    def cell_ids(self, value):
        if not isinstance(value, list):
            raise ValueError('cell_ids must be a list')
        for i in range(len(value)):
            if not isinstance(value[i], int):
                raise ValueError('cell_ids must be a list of int')
        self._cell_ids = value

    @property
    def subpart_ids(self):
        return self._subpart_ids

    @subpart_ids.setter
    def subpart_ids(self, value):
        if not isinstance(value, list):
            raise ValueError('subpart_ids must be a list')
        for i in range(len(value)):
            if not isinstance(value[i], str):
                raise ValueError('subpart_ids must be a list of string')
        self._subpart_ids = value

    @property
    def part_cell_list(self):
        return self._part_cell_list

    @part_cell_list.setter
    def part_cell_list(self, value):
        if not isinstance(value, list):
            raise ValueError('part_cell_list must be a list')
        for i in range(len(value)):
            if not isinstance(value[i], Cell):
                raise ValueError('part_cell_ist must be a list of Cell')
        self._part_cell_list = value

    @property
    def part_subpart_list(self):
        return self._part_cell_list

    @part_subpart_list.setter
    def part_subpart_list(self, value):
        if not isinstance(value, list):
            raise ValueError('part_subpart_list must be a list')
        for i in range(len(value)):
            if not isinstance(value[i], Part):
                raise ValueError('part_subpart_ist must be a list of Cell')
        self._part_subpart_list = value

    @property
    def mass_flow_rate(self):
        return self._mass_flow_rate

    @mass_flow_rate.setter
    def mass_flow_rate(self, value):
        if not isinstance(value, float):
            raise ValueError('mass flow rate of the part must be float')
        if value < 0.0:
            raise ValueError('mass flow rate must >= 0.0')
        self._mass_flow_rate = value

    @property
    def node_part_count(self):
        return self._node_part_count

    @node_part_count.setter
    def node_part_count(self, value):
        if not isinstance(value, list) and not isinstance(value, np.ndarray):
            raise ValueError('node_part_count must be a list')
        for i in range(len(value)):
            if not isinstance(value[i], int) and not isinstance(value[i], np.int64):
                raise ValueError('node_part_count must be a list of int')
        self._node_part_count = value

    @property
    def equal_cell(self):
        return self._equal_cell

    def init_equal_cell(self):
        """
        Calculate the equal_cell:
        - name (use part name)
        - vol (sum)
        - mass (sum) 
        - density (average)
        - neutron flux (vol average)
        """
        self._equal_cell = Cell()
        self._equal_cell.name = self.name
        # check part_cell_list
        if len(self.part_cell_list) >= 1:
            # merge basic info. vol, mass and density
            for c in self.part_cell_list:  # vol and mass
                self.equal_cell.vol += c.vol
                self.equal_cell.mass += c.mass
            self.equal_cell.density = self.equal_cell.mass / self.equal_cell.vol  # density
            # neutron flux
            ave_flux = [0.0] * len(self.part_cell_list[0].neutron_flux)
            for i, c in enumerate(self.part_cell_list):
                for j in range(len(ave_flux)):
                    ave_flux[j] += c.vol / \
                        self.equal_cell.vol * c.neutron_flux[j]
            self.equal_cell.neutron_flux = ave_flux

    def merge_cell(self, AIM):
        """merge_cell: a method of class Part
        funciton: merge the part_cell_list to make a equivalent cell
        data need to merge: basic: vol, mass, density
                            result data: nuclide, half_life, act, decay_heat, ...
                            contact_dose, ci, dpa, He_production, H_production"""
        # chech AIM
        if AIM not in ('CELL_ACT_POST', 'CELL_DPA_POST'):
            raise ValueError(
                'Part.merge_cell() can only be called when the AIM is CELL_ACT/DPA_POST')
        if AIM == 'CELL_ACT_POST':
            # treat nuclide and half_life
            for c in self._part_cell_list:
                for i, nuc in enumerate(c.nuclide):
                    if nuc in self._equal_cell.nuclide:
                        pass
                    if nuc not in self._equal_cell.nuclide:
                        self._equal_cell.nuclide.append(nuc)
                        self._equal_cell.half_life.append(c.half_life[i])
            # treat act, decay_heat, contact_dose and ci
            # first, resize the act, decay_heat, contact_dose and ci
            NUC = len(self._equal_cell.nuclide)
            INTV = self._part_cell_list[0].act.shape[0]
            self._equal_cell.act = np.resize(self._equal_cell.act, (INTV, NUC))
            self._equal_cell.total_alpha_act = np.resize(
                self._equal_cell.total_alpha_act, (INTV))
            self._equal_cell.decay_heat = np.resize(
                self._equal_cell.decay_heat, (INTV, NUC))
            self._equal_cell.contact_dose = np.resize(
                self._equal_cell.contact_dose, (INTV, NUC))
            self._equal_cell.ci = np.resize(self._equal_cell.ci, (INTV, NUC))
            # merge the data
            for c in self._part_cell_list:
                for i, nuc in enumerate(c.nuclide):
                    nid = self._equal_cell._nuclide.index(nuc)
                    for intv in range(INTV):
                        self._equal_cell.act[intv][nid] += c.act[intv][i] * (
                            c.mass / self._equal_cell.mass)  # unit: Bq/kg
                        self._equal_cell.decay_heat[intv][nid] += c.decay_heat[intv][i] * (
                            c.mass / self._equal_cell.mass)  # kW/kg
                        self._equal_cell.contact_dose[intv][nid] += c.contact_dose[intv][i] * (
                            c.mass / self._equal_cell.mass)  # unit: Sv/h
                        self._equal_cell.ci[intv][nid] += c.ci[intv][i] * \
                            (c.mass / self._equal_cell.mass)
                for intv in range(INTV):
                    self._equal_cell.total_alpha_act[intv] += c.total_alpha_act[intv] * (
                        c.mass / self._equal_cell.mass)
        if AIM == 'CELL_DPA_POST':
            # dpa and gas production
            dpa, He_production, H_production = 0.0, 0.0, 0.0
            for c in self._part_cell_list:
                dpa += c.dpa * (c.mass / self._equal_cell.mass)
                He_production += c.He_production * \
                    (c.mass / self._equal_cell.mass)
                H_production += c.H_production * \
                    (c.mass / self._equal_cell.mass)
            self._equal_cell.dpa = dpa
            self._equal_cell.He_production = He_production
            self._equal_cell.H_production = H_production

    def part_act_analysis(self, AIM, rwss=[]):
        """
        Analysis the:
        - acitivty,
        - contact_dose,
        - decay_heat,
        - ci,
        - radwaste class (optional),
        of the Part, using the method the Cell.

        Parameters:
        -----------
        AIM: AIM, must be 'CELL_ACT_POST'
        rwss: list of RadwasteStandard, optional
            The standards used.
            Supported standards are: CHN2018, UK, USNRC, USNRC_FETTER.
        """

        # AIM check
        if AIM not in ['CELL_ACT_POST']:
            raise ValueError(
                'method act_analysis() of a Part should be called only when the AIM is CELL_ACT_POST')
        # data prepare check
        if self._equal_cell.act.shape[0] < 1:
            raise ValueError(
                'method act_alalysis() should be called after filling the data of act')
        # analysis the act info.
        # calculate the act_max_nuc, act_max_act and act_max_ratio
        self._equal_cell.analysis_act()
        # analysis the decay_heat
        self._equal_cell.analysis_decay_heat()
        # analysis the contact_dose
        self._equal_cell.analysis_contact_dose()
        # analysis the ci
        self._equal_cell.analysis_ci()
        # analysis radwaste classification
        for rws in rwss:
            self._equal_cell.analysis_radwaste(rws=rws)

    def generate_directory(self, WORK_DIR):
        """
        Generate directory name for output files.
        """
        self.dirname = os.path.join(WORK_DIR, self._name)
        if not os.path.isdir(self.dirname):
            os.mkdir(self.dirname)

    def generate_output_filename(self, item):
        """
        Create output filename for specific file.
        """
        filename = os.path.join(self.dirname, ''.join([self._name, '.', item]))
        return filename

    def generate_output_title_line(self, item):
        """
        Generate output file title line for each item.
        """
        title_line = None
        # input item check
        if item == 'basicinfo':
            title_line = utils.data_to_line_1d(
                key=self._name, value='basic_information')
        if item == 'nuc':
            title_line = utils.data_to_line_1d(
                key='Nuclide', value='Half_life(s)')
        if item in ['acts', 'act', 'dhv', 'dh', 'cd', 'ci']:
            title_line = utils.data_to_line_1d(
                key='Cooling_time(s)', value=self._equal_cell.nuclide)
        if item in ['act_st_t']:
            value = ['total_specific_act(Bq/kg)', 'total_activity(Bq)']
            title_line = utils.data_to_line_1d(
                key='Cooling_time(s)', value=value)
        if item in ['acts_max_ratio']:
            title_line = utils.data_to_line_1d(
                key='Cooling_time(s)', value=self._equal_cell.act_max_contri_nuc)
        if item in ['acts_max']:
            title_line = utils.data_to_line_1d(key='Cooling_time(s)', value=[
                                               'Total'] + self._equal_cell.act_max_contri_nuc)
        if item in ['dh_vt_t']:
            value = ['total_decay_heat_vol(kW/m3)',
                     'total_decay_heat(kW)']
            title_line = utils.data_to_line_1d(
                key='Cooling_time(s)', value=value)
        if item in ['dhv_max']:
            title_line = utils.data_to_line_1d(key='Cooling_time(s)', value=[
                                               'Total'] + self._equal_cell.decay_heat_max_contri_nuc)
        if item in ['dhv_max_ratio']:
            title_line = utils.data_to_line_1d(
                key='Cooling_time(s)', value=self._equal_cell.decay_heat_max_contri_nuc)
        if item in ['cdt']:
            title_line = utils.data_to_line_1d(
                key='Cooling_time(s)', value='total_contact_dose(Sv/hr)')
        if item in ['cd_max']:
            title_line = utils.data_to_line_1d(key='Cooling_time(s)', value=[
                                               'Total'] + self._equal_cell.contact_dose_max_contri_nuc)
        if item in ['cd_max_ratio']:
            title_line = utils.data_to_line_1d(
                key='Cooling_time(s)', value=self._equal_cell.contact_dose_max_contri_nuc)
        if item in ['cit']:
            title_line = utils.data_to_line_1d(
                key='Cooling_time(s)', value=['total_ci'])
        if item in ['ci_max']:
            title_line = utils.data_to_line_1d(
                key='Cooling_time(s)', value=self._equal_cell.ci_max_contri_nuc)
        if item in ['ci_max_ratio']:
            title_line = utils.data_to_line_1d(key='Cooling_time(s)', value=[
                                               'Total'] + self._equal_cell.ci_max_contri_nuc)
        if item in ['gamma_emit_rate']:
            title_line = utils.data_to_line_1d(key='Energy upper boundary (MeV)', value=[
                                               'Gamma emit rate (g/cc/s)'])
        if title_line is None:  # check
            raise ValueError("item {0} is not supported".format(item))
        return title_line

    def output_item(self, item, key, value):
        """
        Output item.

        Parameters:
        -----------
        item: string
            The postfix of the file.
        key: string, list or numpy array
            The key first column of the of the data.
        value: float, list or numpy array
            The data of the content to print.
        """
        filename = self.generate_output_filename(item)
        fo = open(filename, 'w')
        title_line = self.generate_output_title_line(item)
        fo.write(title_line)
        if isinstance(key, list) or isinstance(key, np.ndarray):
            for i in range(len(key)):
                line = utils.data_to_line_1d(key=key[i], value=value[i])
                fo.write(line)
        else:
            line = utils.data_to_line_1d(key=key, value=value)
            fo.write(line)
        fo.close()

    def output_basicinfo(self, MODEL_DEGREE, cooling_times_cul):
        """
        Output basic infomation.
        """
        item = 'basicinfo'
        key = ["volume(cm3)", "mass(g)", "density(g/cm3)"]
        value = [self._equal_cell.vol * 360.0 / MODEL_DEGREE,
                 self._equal_cell.mass * 360.0 / MODEL_DEGREE,
                 self._equal_cell.density]
        self.output_item(item=item, key=key, value=value)

    def output_flux(self):
        """Output flux"""
        # write .flx file
        filename = self.generate_output_filename('flx')
        fo = open(filename, 'w')
        for i in range(len(self.equal_cell.neutron_flux) - 1):
            flux = self.equal_cell.neutron_flux[len(
                self.equal_cell.neutron_flux)-2-i]
            fo.write(
                f"{utils.format_single_output(flux)}\n")
        fo.write("1.0\n")
        fo.write(
            f"Neutron energy group 175 G, TOT = {self.equal_cell.neutron_flux[-1]}")
        fo.close()

        # write .flux file
        filename = self.generate_output_filename('flux')
        fo = open(filename, 'w')
        for i in range(len(self.equal_cell.neutron_flux) - 1):
            fo.write(
                f"{utils.format_single_output(self.equal_cell.neutron_flux[i])}\n")
        fo.close()

    def output_nuc(self):
        # output nuclide & half_life
        item = 'nuc'
        key = self._equal_cell.nuclide
        value = self._equal_cell.half_life
        self.output_item(item=item, key=key, value=value)

    def output_acts(self, cooling_times_cul):
        # output specific activity info. unit Bq/kg
        item = 'acts'
        key = cooling_times_cul
        value = self._equal_cell.act
        self.output_item(item=item, key=key, value=value)

    def output_act(self, MODEL_DEGREE, cooling_times_cul):
        item = 'act'
        key = cooling_times_cul
        value = np.multiply(self._equal_cell.act, 360.0 /
                            MODEL_DEGREE*self._equal_cell.mass/1e3)
        self.output_item(item=item, key=key, value=value)

    def output_act_st_t(self, MODEL_DEGREE, cooling_times_cul):
        item = 'act_st_t'
        key = cooling_times_cul
        value = np.array([self._equal_cell.total_act,
                          np.multiply(np.array(self._equal_cell.total_act),
                                      self._equal_cell.mass / 1e3 * 360.0 / MODEL_DEGREE)
                          ])
        value = value.transpose().copy()
        self.output_item(item, key=key, value=value)

    def output_acts_max(self, cooling_times_cul):
        item = 'acts_max'
        key = cooling_times_cul
        value = np.concatenate((np.array([self._equal_cell.total_act]).transpose(),
                                self._equal_cell.act_max_contri_act), axis=1)
        self.output_item(item=item, key=key, value=value)

    def output_acts_max_ratio(self, cooling_times_cul):
        item = 'acts_max_ratio'
        key = cooling_times_cul
        value = self._equal_cell.act_max_contri_ratio
        self.output_item(item=item, key=key, value=value)

    def output_dhv(self, cooling_times_cul, factor):
        item = 'dhv'
        key = cooling_times_cul
        value = np.multiply(self._equal_cell.decay_heat, factor)
        self.output_item(item=item, key=key, value=value)

    def output_dh(self, cooling_times_cul, factor):
        item = 'dh'
        key = cooling_times_cul
        value = np.multiply(self._equal_cell.decay_heat, factor)
        self.output_item(item=item, key=key, value=value)

    def output_dh_vt_t(self, cooling_times_cul, factor1, factor2):
        item = 'dh_vt_t'
        key = cooling_times_cul
        value = np.array([np.multiply(self._equal_cell.total_decay_heat, factor1),
                          np.multiply(
                              np.array(self._equal_cell.total_decay_heat), factor2)
                          ])
        value = value.transpose().copy()
        self.output_item(item=item, key=key, value=value)

    def output_dhv_max(self, cooling_times_cul, factor):
        item = 'dhv_max'
        key = cooling_times_cul
        value = np.concatenate((np.array([self._equal_cell.total_decay_heat]).transpose(),
                                self._equal_cell.decay_heat_max_contri_dh), axis=1)
        value = np.multiply(value, factor)
        self.output_item(item=item, key=key, value=value)

    def output_dhv_max_ratio(self, cooling_times_cul):
        item = 'dhv_max_ratio'
        key = cooling_times_cul
        value = self._equal_cell.decay_heat_max_contri_ratio
        self.output_item(item=item, key=key, value=value)

    def output_cdt(self, cooling_times_cul):
        item = 'cdt'
        key = cooling_times_cul
        value = self._equal_cell.total_contact_dose
        self.output_item(item=item, key=key, value=value)

    def output_cd(self, cooling_times_cul):
        item = 'cd'
        key = cooling_times_cul
        value = self._equal_cell.contact_dose
        self.output_item(item=item, key=key, value=value)

    def output_cd_max(self, cooling_times_cul):
        item = 'cd_max'
        key = cooling_times_cul
        value = np.concatenate((np.array([self._equal_cell.total_contact_dose]).transpose(),
                                self._equal_cell.contact_dose_max_contri_cd), axis=1)
        self.output_item(item=item, key=key, value=value)

    def output_cd_max_ratio(self, cooling_times_cul):
        item = 'cd_max_ratio'
        key = cooling_times_cul
        value = self._equal_cell.contact_dose_max_contri_ratio
        self.output_item(item=item, key=key, value=value)

    def output_ci(self, cooling_times_cul):
        item = 'ci'
        key = cooling_times_cul
        value = self._equal_cell.ci
        self.output_item(item=item, key=key, value=value)

    def output_cit(self, cooling_times_cul):
        item = 'cit'
        key = cooling_times_cul
        value = np.array([self._equal_cell.total_ci])
        value = value.transpose().copy()
        self.output_item(item=item, key=key, value=value)

    def output_ci_max(self, cooling_times_cul):
        item = 'ci_max'
        key = cooling_times_cul
        value = np.concatenate((np.array([self._equal_cell.total_ci]).transpose(),
                                self._equal_cell.ci_max_contri_ci), axis=1)
        self.output_item(item=item, key=key, value=value)

    def output_ci_max_ratio(self, cooling_times_cul):
        item = 'ci_max_ratio'
        key = cooling_times_cul
        value = self._equal_cell.ci_max_contri_ratio
        self.output_item(item=item, key=key, value=value)

    def output_gamma_emit_rate(self, gamma_energy_upper_bounds):
        item = 'gamma_emit_rate'
        key = gamma_energy_upper_bounds
        value = self.equal_cell.gamma_emit_rate[0]
        self.output_item(item=item, key=key, value=value)

    def output_data(self, WORK_DIR, MODEL_DEGREE, AIM, cooling_times_cul=None,
                    rwss=[]):
        """
        Outputdata: output corresponding information according to the AIM and MODEL_DEGREE
        case 1: AIM = CELL_ACT_POST
            - output basic info. :vol, mass, density
            - nuclide info. : nuclide, half_life
            - act info. :nuclide, act
            - act_max_contri_nuc & act_max_contri_act
            - act_max_contri_nuc & act_max_contri_ratio
            - nuclide & decay_heat
            - decay_heat_max_contri_nuc & decay_heat_max_contri_dh
            - decay_heat_max_contri_nuc & decay_heat_max_contri_ratio
            - total_decay_heat
            - nuclide & contact_dose
            - contact_dose_max_contri_nuc & contact_dose_max_contri_cd
            - contact_dose_max_contri_nuc & contact_dose_max_contri_ratio
            - nuclide & ci
            - ci_max_contri_nuc & ci_max_contri_ci
            - ci_max_contri_nuc & ci_max_contri_ratio
            - radwaste classifcation, optional if rws is not None
        case 2: AIM = CELL_DPA_POST.
            - output basic info. : vol, mass, density
            - dpa,
            - He_production
            - H_production
        """

        # generate directory for this part
        self.generate_directory(WORK_DIR)
        # case 1: AIM == CELL_ACT_POST
        if AIM == 'CELL_ACT_POST':
            # check cooling_times_cul
            if cooling_times_cul is None:
                raise ValueError(
                    "cooling_times_cul must be provided in CELL_ACT_POST mode")
            # output basic info.
            self.output_basicinfo(MODEL_DEGREE, cooling_times_cul)
            # output nuclide & half_life
            self.output_nuc()
            # output flux
            self.output_flux()

            # -------------------activity part--------------------------------
            # output specific activity info. unit Bq/kg
            self.output_acts(cooling_times_cul)
            # output activity info. unit Bq
            self.output_act(MODEL_DEGREE, cooling_times_cul)
            # total_specific activy and total activity
            self.output_act_st_t(MODEL_DEGREE, cooling_times_cul)
            # output act_max_contri_nuc & act_max_contri_act, unit Bq/kg
            self.output_acts_max(cooling_times_cul)
            # output act_max_contri_nuc & act_max_contri_ratio, unit 1
            self.output_acts_max_ratio(cooling_times_cul)

            # --------------------decay_heat----------------------------------
            # output decay_heat info., unit kW/m3, origin kW/kg
            # unit change factor from kW/kg -> kW/m3
            factor = self._equal_cell.mass / 1.0e3 / \
                (self._equal_cell.vol / 1.0e6)

            def f(x):
                return x * factor
            # decay heat kW/m3
            self.output_dhv(cooling_times_cul, factor)
            # output decay_heat of 360 degree model info. unit kW
            self.output_dh(cooling_times_cul, factor*self._equal_cell.vol/1e6)
            # total hecay_heat
            self.output_dh_vt_t(cooling_times_cul, factor,
                                factor*self._equal_cell.vol/1e6)
            # output decay_heat_max_contri_nuc & decay_heat_max_contri_dh,
            # unit : kW/m3
            self.output_dhv_max(cooling_times_cul, factor)
            # output decay_heat_max_contri_nuc & decay_heat_max_contri_ratio,
            # unit 1
            self.output_dhv_max_ratio(cooling_times_cul)

            # ---------------------contact_dose-------------------------------
            # total contact_dose
            self.output_cdt(cooling_times_cul)
            # contact_dose of each nuc
            self.output_cd(cooling_times_cul)
            # contact_dose_max
            self.output_cd_max(cooling_times_cul)
            # contact_dose_max_ratio
            self.output_cd_max_ratio(cooling_times_cul)

            # ------------------------ci part---------------------------------
            self.output_ci(cooling_times_cul)
            # total ci
            self.output_cit(cooling_times_cul)
            # ci_max
            self.output_ci_max(cooling_times_cul)
            # ci_max_ratio
            self.output_ci_max_ratio(cooling_times_cul)

            # --------------------Radwaste part-------------------------------
            #  radwaste classification chn2018
            for rws in rwss:
                # radwaste classification results
                if rws.standard == 'CHN2018':
                    filename = self.generate_output_filename('rwc_chn2018')
                    line = ','.join(['Cooling_time(s)', 'Radwaste_Class', 'Decay_heat(kW/m3)',
                                     'Clearance', 'VLLW', 'LLW', 'ILW', 'Limit'])
                    fo = open(filename, 'w')
                    fo.write(line+'\n')
                    for intv in range(len(cooling_times_cul)):
                        line = ','.join([utils.format_single_output(cooling_times_cul[intv]),  # cooling time
                                         # rwc
                                         self._equal_cell.radwaste_class_chn2018[intv],
                                         utils.format_single_output(
                                             self._equal_cell.total_decay_heat[intv] * factor),  # decay heat, (kW/m3)
                                         utils.data_to_line_1d(
                                             key=None, value=self._equal_cell.rw_chn2018_index_sum[intv], postfix=''),  # indices
                                         utils.format_single_output(1.0)])  # limit
                        fo.write(line+'\n')
                    fo.close
                elif rws.standard == 'USNRC':
                    filename = self.generate_output_filename('rwc_usnrc')
                    line = ','.join(['Cooling_time(s)', 'Radwaste_Class', 'CI', 'LLWA_LL',
                                     'LLWB_LL', 'LLWC_LL', 'LLWA_SL', 'LLWB_SL', 'LLWC_SL', 'Limit'])
                    fo = open(filename, 'w')
                    fo.write(line+'\n')
                    for intv in range(len(cooling_times_cul)):
                        line = ','.join([utils.format_single_output(cooling_times_cul[intv]),  # cooling time
                                         # rwc
                                         self._equal_cell.radwaste_class_usnrc[intv],
                                         utils.format_single_output(
                                             self._equal_cell.total_ci_usnrc[intv]),
                                         utils.data_to_line_1d(
                                             key=None, value=self._equal_cell.rw_usnrc_index_sum_ll[intv], postfix=''),
                                         utils.data_to_line_1d(
                                             key=None, value=self._equal_cell.rw_usnrc_index_sum_sl[intv], postfix=''),
                                         utils.format_single_output(1.0)])  # limit
                        fo.write(line+'\n')
                    fo.close
                elif rws.standard == 'USNRC_FETTER':
                    filename = self.generate_output_filename(
                        'rwc_usnrc_fetter')
                    line = ','.join(['Cooling_time(s)', 'Radwaste_Class', 'CI', 'LLWA',
                                     'LLWB', 'LLWC', 'Limit'])
                    fo = open(filename, 'w')
                    fo.write(line+'\n')
                    for intv in range(len(cooling_times_cul)):
                        line = ','.join([utils.format_single_output(cooling_times_cul[intv]),  # cooling time
                                         # rwc
                                         self._equal_cell.radwaste_class_usnrc_fetter[intv],
                                         utils.format_single_output(
                                             self._equal_cell.total_ci_usnrc[intv]),
                                         utils.data_to_line_1d(
                                             key=None, value=self._equal_cell.rw_usnrc_fetter_index_sum[intv], postfix=''),
                                         utils.format_single_output(1.0)])  # limit
                        fo.write(line+'\n')
                    fo.close
                elif rws.standard == 'UK':
                    filename = self.generate_output_filename('rwc_uk')
                    line = ','.join(['Cooling_time(s)', 'Radwaste_Class', 'CI', 'Decay_heat(kW/m3)',
                                     'Alpha_act(Bq/kg)', 'Act(Bq/kg)', 'Limit'])
                    fo = open(filename, 'w')
                    fo.write(line+'\n')
                    for intv in range(len(cooling_times_cul)):
                        line = ','.join([utils.format_single_output(cooling_times_cul[intv]),  # cooling time
                                         # rwc
                                         self._equal_cell.radwaste_class_uk[intv],
                                         utils.format_single_output(
                                             self._equal_cell.total_ci[intv]),
                                         utils.format_single_output(
                                             self._equal_cell.total_decay_heat[intv] * factor),  # decay heat, (kW/m3)
                                         utils.format_single_output(
                                             self._equal_cell._total_alpha_act[intv]),  # alpha act
                                         utils.format_single_output(
                                             self._equal_cell._total_act[intv]),  # total act
                                         utils.format_single_output(1.0)])  # limit
                        fo.write(line+'\n')
                    fo.close
                elif rws.standard == 'RUSSIAN':
                    filename = self.generate_output_filename('rwc_russian')
                    line = ','.join(['Cooling_time(s)', 'Radwaste_Class', 'Decay_heat(kW/m3)',
                                     'LLW', 'Limit'])
                    fo = open(filename, 'w')
                    fo.write(line+'\n')
                    for intv in range(len(cooling_times_cul)):
                        line = ','.join([utils.format_single_output(cooling_times_cul[intv]),  # cooling time
                                         # rwc
                                         self._equal_cell.radwaste_class_russian[intv],
                                         utils.format_single_output(
                                             self._equal_cell.total_decay_heat[intv] * factor),  # decay heat, (kW/m3)
                                         utils.data_to_line_1d(
                                             key=None, value=self._equal_cell.rw_russian_index_sum[intv], postfix=''),  # indices
                                         utils.format_single_output(1.0)])  # limit
                        fo.write(line+'\n')
                    fo.close

        # case 2: AIM == CELL_DPA_POST
        # output the dpa information
        if AIM == 'CELL_DPA_POST':
            # output the DPA information
            filename = self.generate_output_filename('dpa')
            fo = open(filename, 'w')
            line = ' '.join(['DPA:', str(self._equal_cell.dpa), 'DPA/FPY\n'])
            fo.write(line)
            line = ' '.join(['He_production:', str(
                self._equal_cell.He_production), 'appm/FPY\n'])
            fo.write(line)
            line = ' '.join(['H_production:', str(
                self._equal_cell.H_production), 'appm/FPY\n'])
            fo.write(line)
            fo.close()

        # case 3: AIM == COOLANT_ACT_POST
        if AIM == 'COOLANT_ACT_POST':
            # output the act, decay_heat, contact_dose
            filename = self.generate_output_filename('coolant_response')
            fo = open(filename, 'w')
            line = utils.data_to_line_1d(
                key='Nuclide', value=self.equal_cell.nuclide)
            fo.write(line)
            line = utils.data_to_line_1d(
                key='Specific act (Bq/kg)', value=self.equal_cell.act[0])
            fo.write(line)
            line = utils.data_to_line_1d(
                key='Decay heat (kW/kg)', value=self.equal_cell.decay_heat[0])
            fo.write(line)
            line = utils.data_to_line_1d(
                key='Contact dose (Sv/h)', value=self.equal_cell.contact_dose[0])
            fo.write(line)
            fo.close()
            # output gamma_emit_rate
            self.output_gamma_emit_rate(gamma_energy_upper_bounds)
            # output neutron_emit_rate
            filename = self.generate_output_filename('neutron_emit_rate')
            fo = open(filename, 'w')
            line = ','.join(['Energy (MeV)', 'Nuetron emit rate (n/kg/s)'])
            fo.write(line+'\n')
            nid = self.equal_cell.nuclide.index('N17')
            line = ','.join(['0.848', utils.format_single_output(
                self.equal_cell.act[0][nid]*0.95)])
            fo.write(line+'\n')
            fo.close()


def get_part_index(parts, p):
    """get the index of part p in the parts"""
    pidx = -1
    for i in range(len(parts)):
        if p.name == parts[i].name:  # found it
            pidx = i
    # check value
    if pidx == -1:
        raise ValueError(f'part {p.name} not found in the parts')
    return pidx


def get_part_index_by_name(parts, name):
    """get the index of part p in the parts"""
    pidx = -1
    for i in range(len(parts)):
        if name == parts[i].name:  # found it
            pidx = i
    # check value
    if pidx == -1:
        raise ValueError(f'part {name} not found in the parts')
    return pidx


def get_part_index_by_cell_id(parts, cid, find_last=False):
    """get the index of part p in parts according to specific cid"""
    pidx = -1
    for i, p in enumerate(parts):
        if cid in p.cell_ids:
            if find_last:
                pidx = i
            else:
                return i
    if pidx == -1:
        raise ValueError(f"cell: {cid} not in parts")
    return pidx


def is_cell_id_in_parts(parts, cid):
    """check whether a cell id is in parts"""
    for i, p in enumerate(parts):
        if cid in p.cell_ids:
            return True
    return False


def is_item_part(item, parts=None):
    """
    Check whether the item means a part.
    The item is a string and exist in Parts.

    Parameters:
    -----------
    item : str
    """
    if not isinstance(item, str):
        return False

    if parts is None:
        return True
    else:
        try:  # check whether item in part list
            pidx = get_part_index_by_name(parts, item)
            return True
        except:
            return False
