#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import numpy as np
from natf import utils
from natf.material import Material


class Cell(object):
    ''' class Cell'''

    def __init__(self, id=None):
        self._name = ''
        self._icl = None
        self._id = id
        self._mid = None
        self._mat = Material()
        self._geom = []  # list of dict of {Boolean:surf_list}
        self._imp_n = 1.0
        self._imp_p = None
        self._vol = 0.0  # cm3
        self._mass = 0.0  # g
        self._density = 0.0  # g/cm3
        self._neutron_flux = np.zeros(0, dtype=float)
        self._neutron_flux_error = np.zeros(0, dtype=float)
        self._gamma_emit_rate = np.zeros((0, 0), dtype=float, order='C')
        self._nuclide = []  # fispact output data nuclide
        self._half_life = []
        # activity part, unit: Bq/kg
        # specific activity of nuclides at different inteval, shape=(INTV, NUC)
        self._act = np.zeros((0, 0), dtype=float, order='C')
        self._act_max_contri_nuc = []  # read only
        # specific activity of max contribution nuclide
        self._act_max_contri_act = np.zeros((0, 0), dtype=float,
                                            order='C')
        self._act_max_contri_ratio = np.zeros((0, 0), dtype=float)
        self._total_act = np.zeros(0, dtype=float)
        self._total_alpha_act = np.zeros((0), dtype=float)
        # decay heat part, unit: kW/kg
        self._decay_heat = np.zeros((0, 0), dtype=float)
        self._decay_heat_max_contri_nuc = []
        self._decay_heat_max_contri_dh = np.zeros((0, 0), dtype=float)
        self._decay_heat_max_contri_ratio = np.zeros((0, 0), dtype=float)
        self._total_decay_heat = np.zeros(0, dtype=float)
        # contact dose part,
        self._contact_dose = np.zeros((0, 0), dtype=float)
        self._contact_dose_max_contri_nuc = []
        self._contact_dose_max_contri_cd = np.zeros((0, 0), dtype=float)
        self._contact_dose_max_contri_ratio = np.zeros((0, 0), dtype=float)
        self._total_contact_dose = []
        # Clear Index part
        self._ci = np.zeros((0, 0), dtype=float)
        self._ci_max_contri_nuc = []
        self._ci_max_contri_ci = np.zeros((0, 0), dtype=float)
        self._ci_max_contri_ratio = np.zeros((0, 0), dtype=float)
        self._total_ci = np.zeros(0, dtype=float)
        # irradiation damage part
        self._dpa = None
        self._He_production = None
        self._H_production = None
        # radwaste part
        # CHN2018
        self._rw_chn2018_index_sum = None
        self._radwaste_class_chn2018 = []
        # USNRC
        self._rw_usnrc_index_sum_ll = None
        self._rw_usnrc_index_sum_sl = None
        self._radwaste_class_usnrc = []
        self._ci_usnrc = np.zeros((0, 0), dtype=float)
        self._total_ci_usnrc = np.zeros(0, dtype=float)
        # USNRC_FETTER
        self._rw_usnrc_fetter_index_sum = None
        self._radwaste_class_usnrc_fetter = []
        # UK
        self._radwaste_class_uk = []
        # RUSSIAN
        self._rw_russian_index_sum = None
        self._radwaste_class_russian = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError('name must be string')
        self._name = value

    # icl getter and setter
    @property
    def icl(self):
        return self._icl

    @icl.setter
    def icl(self, value):
        if not isinstance(value, int):
            raise ValueError('icl must be integer')
        if value < 1 or value > 100000:
            raise ValueError('icl must between 1 and 100000')
        self._icl = value

    # id setter and getter
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if not isinstance(value, int):
            raise ValueError('id must be integer')
        if value < 1 or value > 100000:
            raise ValueError('id must between 1 and 100000')
        self._id = value

    # mid setter and getter
    @property
    def mid(self):
        return self._mid

    @mid.setter
    def mid(self, value):
        if not isinstance(value, int):
            raise ValueError('mid must be integer')
        if value < 0 or value > 100000:
            raise ValueError('mid must between 0 and 100000')
        self._mid = value

    @property
    def mat(self):
        return self._mat

    @mat.setter
    def mat(self, value):
        if not isinstance(value, Material):
            raise ValueError('mat must be a object of class Material')
        self._mat = value

    @property
    def surf_list(self):
        return self._surf_list

    @surf_list.setter
    def self_list(self, value):
        if not isinstance(value, list):
            raise ValueError('surf_list of cell must be a list')
        for i, surf in value:
            if not isinstance(value, int):
                raise ValueError('surf_list should be a list of int')
        self._surf_list = value

    @property
    def surf_sign(self):
        return self._surf_sign

    @surf_sign.setter
    def self_sign(self, value):
        if not isinstance(value, list):
            raise ValueError('surf_sign of cell must be a list')
        for i, surf in value:
            if not isinstance(value, str):
                raise ValueError('surf_sign should be a list of string')
            if value not in ('*', '+', ''):
                raise ValueError('surf sign {0} not support'.format(value))
        self._surf_sign = value

    @property
    def imp_n(self):
        return self._imp_n

    @imp_n.setter
    def imp_n(self, value):
        if value < 0:
            raise ValueError('imp_n must be a number that no smaller than 0')
        self._imp_n = value

    @property
    def imp_p(self):
        return self._imp_p

    @imp_p.setter
    def imp_p(self, value):
        if value < 0:
            raise ValueError('imp_p must be a number that no smaller than 0')
        self._imp_p = value

    @property
    def vol(self):
        return self._vol

    @vol.setter
    def vol(self, value):
        if not isinstance(value, float):
            raise ValueError('vol of cell must be a float')
        if value < 0:
            raise ValueError('vol must be a float that no smaller than 0')
        self._vol = value

    @property
    def mass(self):
        return self._mass

    @mass.setter
    def mass(self, value):
        if not isinstance(value, float):
            raise ValueError('mass of cell must be a float')
        if value < 0:
            raise ValueError('mass of cell must be a float no smaller than 0')
        self._mass = value

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, value):
        if not isinstance(value, float):
            raise ValueError('density of cell must be a float')
        if value < 0 or value > 30:
            raise ValueError('density of cell must between 0 and 30')
        self._density = value

    @property
    def neutron_flux(self):
        return self._neutron_flux

    @neutron_flux.setter
    def neutron_flux(self, value):
        if not isinstance(value, list):
            raise ValueError('nuetron_flux of cell must be a list')
        if len(value) not in [70, 176, 316, 710]:
            raise ValueError('neutron flux should have data of 70/176/316/710, \
                    with the last of total data')
        for i in range(len(value)):
            if not isinstance(value[i], float):
                raise ValueError(
                    'neutron_flux of cell must be a list of float')
            if value[i] < 0:
                raise ValueError('neutron_flux must be a list that each element\
                        is no smaller than 0.0')
        self._neutron_flux = value

    @property
    def neutron_flux_error(self):
        return self._neutron_flux_error

    @neutron_flux_error.setter
    def neutron_flux_error(self, value):
        if not isinstance(value, list):
            raise ValueError('neutron_flux_error must be a list')
        if len(value) not in [70, 176, 316, 710]:
            raise ValueError('neutron flux should have data of 70/176/316/710, \
                    the last of total data')
        for i in range(len(value)):
            if not isinstance(value[i], float):
                raise ValueError('neutron_flux_error must be a list of float')
            if value[i] < 0.0 or value[i] > 1:
                raise ValueError('neutron_flux_error must between 0 and 1')
        self._neutron_flux_error = value

    @property
    def gamma_emit_rate(self):
        return self._gamma_emit_rate

    @gamma_emit_rate.setter
    def gamma_emit_rate(self, value):
        if not isinstance(value, type(np.ndarray((0, 0)))):
            raise ValueError('gamma_emit_rate must be ndarray')
        if len(value.shape) != 2:
            raise ValueError('gamma_emit_rate must be a two-dimensional\
                    ndarray')
        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                if not isinstance(value[i, j], float):
                    raise ValueError('gamma_emit_rate must composed of float')
        if value.min() < 0.0:
            raise ValueError('gamma_emit_rate must no smaller than 0.0')
        self._gamma_emit_rate = value

    @property
    def nuclide(self):
        return self._nuclide

    @nuclide.setter
    def nuclide(self, value):
        if not isinstance(value, list):
            raise ValueError('nuclide of cell must be a list')
        for i in range(len(value)):
            if not isinstance(value[i], str):
                raise ValueError('nuclide of cell should be a list of string')
        self._nuclide = value

    @property
    def half_life(self):
        return self._half_life

    @half_life.setter
    def half_life(self, value):
        if not isinstance(value, list):
            raise ValueError('half_life must a list')
        for i in range(len(value)):
            if not isinstance(value[i], float):
                raise ValueError('half_life of nuclide must be float')
            if value[i] < 0:
                raise ValueError('half_life of nuclide shoule be no smaller\
                        than 0.0')
        self._half_life = value

    @property
    def act(self):
        return self._act

    @act.setter
    def act(self, value):
        if not isinstance(value, type(np.ndarray((0, 0)))):
            raise ValueError('act must be ndarray')
        if len(value.shape) != 2:
            raise ValueError('act must be a two-dimensional ndarray')
        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                if not isinstance(value[i, j], float):
                    raise ValueError('act must composed of float')
        if value.min() < 0.0:
            raise ValueError(
                f'act must no smaller than 0.0, error data {value.min()}')
        self._act = value

    @property
    def act_max_contri_nuc(self):
        return self._act_max_contri_nuc

    @property
    def act_max_contri_act(self):
        return self._act_max_contri_act

    @property
    def act_max_contri_ratio(self):
        return self._act_max_contri_ratio

    @property
    def total_act(self):
        return self._total_act

    @property
    def total_alpha_act(self):
        return self._total_alpha_act

    @total_alpha_act.setter
    def total_alpha_act(self, value):
        if not isinstance(value, type(np.ndarray((0)))):
            raise ValueError('total_alpha_act must be ndarray')
        if len(value.shape) != 1:
            raise ValueError(
                'total_alpha_act must be a one-dimensional ndarray')
        for i in range(value.shape[0]):
            if not isinstance(value[i], float):
                raise ValueError('total_alpha_act must composed of float')
        if value.min() < 0.0:
            raise ValueError('total_alpha_act must no smaller than 0.0')
        self._total_alpha_act = value

    @property
    def decay_heat(self):
        return self._decay_heat

    @decay_heat.setter
    def decay_heat(self, value):
        if not isinstance(value, type(np.ndarray((0, 0)))):
            raise ValueError('act must be ndarray')
        if len(value.shape) != 2:
            raise ValueError('act must be a two-dimensional ndarray')
        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                if not isinstance(value[i, j], float):
                    raise ValueError('act must composed of float')
        if value.min() < 0.0:
            raise ValueError('act must no smaller than 0.0')
        self._decay_heat = value

    @property
    def decay_heat_max_contri_nuc(self):
        return self._decay_heat_max_contri_nuc

    @property
    def decay_heat_max_contri_dh(self):
        return self._decay_heat_max_contri_dh

    @property
    def decay_heat_max_contri_ratio(self):
        return self._decay_heat_max_contri_ratio

    @property
    def total_decay_heat(self):
        return self._total_decay_heat

    @property
    def contact_dose(self):
        return self._contact_dose

    @contact_dose.setter
    def contact_dose(self, value):
        if not isinstance(value, type(np.ndarray((0, 0)))):
            raise ValueError('contact_dose must be ndarray')
        if len(value.shape) != 2:
            raise ValueError('contact_dose must be a two-dimensional ndarray')
        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                if not isinstance(value[i, j], float):
                    raise ValueError('contact_dose must composed of float')
        if value.min() < 0.0:
            raise ValueError('contact_dose must no smaller than 0.0')
        self._contact_dose = value

    @property
    def contact_dose_max_contri_nuc(self):
        return self._contact_dose_max_contri_nuc

    @property
    def contact_dose_max_contri_cd(self):
        return self._contact_dose_max_contri_cd

    @property
    def contact_dose_max_contri_ratio(self):
        return self._contact_dose_max_contri_ratio

    @property
    def total_contact_dose(self):
        return self._total_contact_dose

    @property
    def ci(self):
        return self._ci

    @ci.setter
    def ci(self, value):
        if not isinstance(value, type(np.ndarray((0, 0)))):
            raise ValueError('ci must be ndarray')
        if len(value.shape) != 2:
            raise ValueError('ci must be a two-dimensional ndarray')
        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                if not isinstance(value[i, j], float):
                    raise ValueError('ci must composed of float')
        if value.min() < 0.0:
            raise ValueError('ci must no smaller than 0.0')
        self._ci = value

    @property
    def ci_max_contri_nuc(self):
        return self._ci_max_contri_nuc

    @property
    def ci_max_contri_ci(self):
        return self._ci_max_contri_ci

    @property
    def ci_max_contri_ratio(self):
        return self._ci_max_contri_ratio

    @property
    def total_ci(self):
        return self._total_ci

    @property
    def ci_usnrc(self):
        return self._ci_usnrc

    @ci_usnrc.setter
    def ci_usnrc(self, value):
        if not isinstance(value, type(np.ndarray((0, 0)))):
            raise ValueError('ci_usnrc must be ndarray')
        if len(value.shape) != 2:
            raise ValueError('ci_usnrc must be a two-dimensional ndarray')
        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                if not isinstance(value[i, j], float):
                    raise ValueError('ci_usnrc must composed of float')
        if value.min() < 0.0:
            raise ValueError('ci_usnrc must no smaller than 0.0')
        self._ci_usnrc = value

    @property
    def total_ci_usnrc(self):
        return self._total_ci_usnrc

    @property
    def dpa(self):
        return self._dpa

    @dpa.setter
    def dpa(self, value):
        if not isinstance(value, float):
            raise ValueError('dpa value must be a float number')
        if value < 0:
            raise ValueError('dpa value must no smaller than 0.0')
        self._dpa = value

    @property
    def He_production(self):
        return self._He_production

    @He_production.setter
    def He_production(self, value):
        if not isinstance(value, float):
            raise ValueError('He_production value must be a float number')
        if value < 0:
            raise ValueError('He_production value must no smaller than 0.0')
        self._He_production = value

    @property
    def H_production(self):
        return self._H_production

    @H_production.setter
    def H_production(self, value):
        if not isinstance(value, float):
            raise ValueError('H_production value must be a float number')
        if value < 0:
            raise ValueError('H_production value must no smaller than 0.0')
        self._H_production = value

    def analysis_act(self):
        """get the act_max_contri_nuc, act_max_contri_act and
        act_max_contri_ratio"""
        # input check for nuclide, a
        if self._act.size == 0:
            raise ValueError('act must assignment before calculate the\
                    total_act')
        self._total_act = self._act.sum(axis=1)  # calculate the a_total
        # get the max nuclide
        for i in range(self._act.shape[0]):
            nid = np.where(self._act[i] == np.max(self._act[i]))
            nid = _pick_max_ind_from_tuple(nid)
            # judge whether this nuclide exis in the list
            if self._nuclide[nid] not in self._act_max_contri_nuc:
                self._act_max_contri_nuc.append(self._nuclide[nid])
                # cal the act_max_contri_act
                if i == 0:
                    self._act_max_contri_act = self._act[:, nid]
                    self._act_max_contri_act = np.column_stack(
                        (self._act_max_contri_act, self._act[:, nid]))
                    self._act_max_contri_act = np.delete(
                        self._act_max_contri_act, 1, axis=1)
                else:
                    self._act_max_contri_act = np.column_stack((
                        self._act_max_contri_act, self._act[:, nid]))
        # cal the act_max_contri_ratio
        self._act_max_contri_ratio = self._act_max_contri_act.copy()
        for i in range(self._act_max_contri_act.shape[0]):
            for j in range(self._act_max_contri_act.shape[1]):
                self._act_max_contri_ratio[i][j] = \
                    self._act_max_contri_act[i][j] / self._total_act[i]

    @property
    def rw_chn2018_index_sum(self):
        return self._rw_chn2018_index_sum

    @rw_chn2018_index_sum.setter
    def rw_chn2018_index_sum(self, value):
        if not isinstance(value, type(np.ndarray((0, 0)))):
            raise ValueError('rw_chn2018_index_sum must be ndarray')
        if len(value.shape) != 2:
            raise ValueError(
                'rw_chn2018_index_sum must be a two-dimensional ndarray')
        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                if not isinstance(value[i, j], float):
                    raise ValueError(
                        'rw_chn2018_index_sum must composed of float')
        if value.min() < 0.0:
            raise ValueError('rw_chn2018_index_sum must no smaller than 0.0')
        self._rw_chn2018_index_sum = value

    @property
    def rw_usnrc_index_sum_ll(self):
        return self._rw_usnrc_index_sum_ll

    @rw_usnrc_index_sum_ll.setter
    def rw_usnrc_index_sum_ll(self, value):
        if not isinstance(value, type(np.ndarray((0, 0)))):
            raise ValueError('rw_usnrc_index_sum_ll must be ndarray')
        if len(value.shape) != 2:
            raise ValueError(
                'rw_usnrc_index_sum_ll must be a two-dimensional ndarray')
        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                if not isinstance(value[i, j], float):
                    raise ValueError(
                        'rw_usnrc_index_sum_ll must composed of float')
        if value.min() < 0.0:
            raise ValueError('rw_usnrc_index_sum_ll must no smaller than 0.0')
        self._rw_usnrc_index_sum_ll = value

    @property
    def rw_usnrc_index_sum_sl(self):
        return self._rw_usnrc_index_sum_sl

    @rw_usnrc_index_sum_sl.setter
    def rw_usnrc_index_sum_sl(self, value):
        if not isinstance(value, type(np.ndarray((0, 0)))):
            raise ValueError('rw_usnrc_index_sum_sl must be ndarray')
        if len(value.shape) != 2:
            raise ValueError(
                'rw_usnrc_index_sum_sl must be a two-dimensional ndarray')
        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                if not isinstance(value[i, j], float):
                    raise ValueError(
                        'rw_usnrc_index_sum_sl must composed of float')
        if value.min() < 0.0:
            raise ValueError('rw_usnrc_index_sum_sl must no smaller than 0.0')
        self._rw_usnrc_index_sum_sl = value

    @property
    def rw_usnrc_fetter_index_sum(self):
        return self._rw_usnrc_fetter_index_sum

    @rw_usnrc_fetter_index_sum.setter
    def rw_usnrc_fetter_index_sum(self, value):
        if not isinstance(value, type(np.ndarray((0, 0)))):
            raise ValueError('rw_usnrc_fetter_index_sum must be ndarray')
        if len(value.shape) != 2:
            raise ValueError(
                'rw_usnrc_fetter_index_sum must be a two-dimensional ndarray')
        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                if not isinstance(value[i, j], float):
                    raise ValueError(
                        'rw_usnrc_fetter_index_sum must composed of float')
        if value.min() < 0.0:
            raise ValueError(
                'rw_usnrc_fetter_index_sum must no smaller than 0.0')
        self._rw_usnrc_fetter_index_sum = value

    @property
    def rw_russian_index_sum(self):
        return self._rw_russian_index_sum

    @rw_russian_index_sum.setter
    def rw_russian_index_sum(self, value):
        if not isinstance(value, type(np.ndarray((0, 0)))):
            raise ValueError('rw_russian_index_sum must be ndarray')
        if len(value.shape) != 2:
            raise ValueError(
                'rw_russian_index_sum must be a two-dimensional ndarray')
        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                if not isinstance(value[i, j], float):
                    raise ValueError(
                        'rw_russian_index_sum must composed of float')
        if value.min() < 0.0:
            raise ValueError('rw_russian_index_sum must no smaller than 0.0')
        self._rw_russian_index_sum = value

    def update_material(self, mat):
        """
        Update material information from given material.
        The mid, mat, density will be updated.
        """
        self._mat = mat
        self._mid = mat.id
        self._density = mat.density
        return

    def treat_nuc_responses(self, nuc, level):
        """
        Reset the property of the [nuc] to specific [level]. And adjust the
        corresponding total values.
        """
        nidx = self.nuclide.index(nuc)  # find nuc index
        for intv in range(len(self.act)):
            self.act[intv, nidx] = self.act[intv, nidx] * level
            self.decay_heat[intv, nidx] = self.decay_heat[intv, nidx] * level
            self.contact_dose[intv,
                              nidx] = self.contact_dose[intv, nidx] * level
            self.ci[intv, nidx] = self.ci[intv, nidx] * level

    def analysis_decay_heat(self):
        # input check for nuclide,
        if self._decay_heat.size == 0:
            raise ValueError('decay_heat must assignment before calculate the\
                    total_act')
        # calculate the a_total
        self._total_decay_heat = self._decay_heat.sum(axis=1)
        # get the max nuclide
        for i in range(self._decay_heat.shape[0]):
            nid = np.where(self._decay_heat[i] == np.max(self._decay_heat[i]))
            nid = _pick_max_ind_from_tuple(nid)
            # judge whether this nuclide exis in the list
            if self._nuclide[nid] not in self._decay_heat_max_contri_nuc:
                self._decay_heat_max_contri_nuc.append(self._nuclide[nid])
                # cal the act_max_contri_hd
                if i == 0:
                    self._decay_heat_max_contri_dh = self._decay_heat[:, nid]
                    self._decay_heat_max_contri_dh = np.column_stack(
                        (self._decay_heat_max_contri_dh,
                            self._decay_heat[:, nid]))
                    self._decay_heat_max_contri_dh = np.delete(
                        self._decay_heat_max_contri_dh, 1, axis=1)
                else:
                    self._decay_heat_max_contri_dh = np.column_stack(
                        (self._decay_heat_max_contri_dh,
                            self._decay_heat[:, nid]))
        # cal the act_max_contri_ratio
        self._decay_heat_max_contri_ratio = \
            self._decay_heat_max_contri_dh.copy()
        for i in range(self._decay_heat_max_contri_dh.shape[0]):
            for j in range(self._decay_heat_max_contri_dh.shape[1]):
                self._decay_heat_max_contri_ratio[i][j] = \
                    self._decay_heat_max_contri_dh[i][j] / \
                    self._total_decay_heat[i]

    def analysis_contact_dose(self):
        # input check for nuclide,
        if self._contact_dose.size == 0:
            raise ValueError('contact_dose must assignment before calculate \
                    the total_act')
        # calculate the a_total
        self._total_contact_dose = self._contact_dose.sum(axis=1)
        # get the max nuclide
        for i in range(self._contact_dose.shape[0]):
            nid = np.where(self._contact_dose[i] == np.max(
                self._contact_dose[i]))
            nid = _pick_max_ind_from_tuple(nid)
            # judge whether this nuclide exis in the list
            if self._nuclide[nid] not in self._contact_dose_max_contri_nuc:
                self._contact_dose_max_contri_nuc.append(self._nuclide[nid])
                # cal the act_max_contri_hd
                if i == 0:
                    self._contact_dose_max_contri_cd = \
                        self._contact_dose[:, nid]
                    self._contact_dose_max_contri_cd = np.column_stack(
                        (self._contact_dose_max_contri_cd,
                         self._contact_dose[:, nid]))
                    self._contact_dose_max_contri_cd = \
                        np.delete(self._contact_dose_max_contri_cd, 1,
                                  axis=1)
                else:
                    self._contact_dose_max_contri_cd = np.column_stack(
                        (self._contact_dose_max_contri_cd,
                         self._contact_dose[:, nid]))
        # cal the act_max_contri_ratio
        self._contact_dose_max_contri_ratio = \
            self._contact_dose_max_contri_cd.copy()
        for i in range(self._contact_dose_max_contri_cd.shape[0]):
            for j in range(self._contact_dose_max_contri_cd.shape[1]):
                self._contact_dose_max_contri_ratio[i][j] = \
                    self._contact_dose_max_contri_cd[i][j] / \
                    self._total_contact_dose[i]

    def analysis_ci(self):
        # input check for nuclide, a
        if self._ci.size == 0:
            raise ValueError(
                'ci must assignment before calculate the total_ci')
        self._total_ci = self._ci.sum(axis=1)  # calculate the a_total
        # get the max nuclide
        for i in range(self._ci.shape[0]):
            nid = np.where(self._ci[i] == np.max(self._ci[i]))
            nid = _pick_max_ind_from_tuple(nid)
            # judge whether this nuclide exis in the list
            if self._nuclide[nid] not in self._ci_max_contri_nuc:
                self._ci_max_contri_nuc.append(self._nuclide[nid])
                # cal the ci_max_contri_ci
                if i == 0:
                    self._ci_max_contri_ci = self._ci[:, nid]
                    self._ci_max_contri_ci = np.column_stack(
                        (self._ci_max_contri_ci, self._ci[:, nid]))
                    self._ci_max_contri_ci = np.delete(self._ci_max_contri_ci,
                                                       1, axis=1)
                else:
                    self._ci_max_contri_ci = np.column_stack((
                        self._ci_max_contri_ci, self._ci[:, nid]))
        # cal the ci_max_contri_ratio
        self._ci_max_contri_ratio = self._ci_max_contri_ci.copy()
        for i in range(self._ci_max_contri_ci.shape[0]):
            for j in range(self._ci_max_contri_ci.shape[1]):
                self._ci_max_contri_ratio[i][j] = \
                    self._ci_max_contri_ci[i][j] / self._total_ci[i]

    def analysis_radwaste(self, rws=None):
        """
        Analysis the radwaste classification.

        Parameters:
        -----------
        rws: RadwasteStandard
            The standard used.
            Supported standards are: CHN2018, UK, USNRC, USNRC_FETTER, RUSSIAN.
        """
        if rws.standard == 'CHN2018':
            self.analysis_radwaste_chn2018(rws)
        elif rws.standard == 'USNRC':
            self.analysis_radwaste_usnrc(rws)
        elif rws.standard == 'USNRC_FETTER':
            self.analysis_radwaste_usnrc_fetter(rws)
        elif rws.standard == 'UK':
            self.analysis_radwaste_uk(rws)
        elif rws.standard == 'RUSSIAN':
            self.analysis_radwaste_russian(rws)
        else:
            raise ValueError("rws {0} not supported!".format(rws.standard))

    def analysis_radwaste_chn2018(self, rws=None):
        """
        Analysis the radwaste classification.

        Parameters:
        -----------
        rws: RadwasteStandard
            The standard used, must be CHN2018.
        """

        # init rw_index with shape of (INTV, NUC, class)
        rw_index = np.zeros(shape=(len(self.act),
                                   len(self.act[0]), len(rws.classes)), dtype=float)

        # calculate radwaste index for each nuclide
        for nid, nuc in enumerate(self.nuclide):
            # get the limits for the nuclide
            limits = rws.get_nuc_limits(nuc=nuc)
            # loop over the interval
            for intv in range(len(self.act)):
                # calculate the index for each class
                rw_index[intv, nid, :] = np.divide(self.act[intv, nid], limits)

        # sum up the index for each nuclide, shape=(INTV, class)
        rw_index_sum = np.sum(rw_index, axis=1)

        # get the radwaste classification according to the indices for each class
        rw_class = []
        for intv in range(len(self.act)):
            # CHN2018 use rw_index_sum and decay heat to classify radwaste
            # convert decay heat from kW/kg to kW/m3
            decay_heat = self.total_decay_heat[intv]  # kW/kg
            decay_heat = decay_heat * self.density * 1000.0  # kW/m3
            rw_class.append(rws.determine_class_chn2018(rw_index_sum[intv],
                                                        decay_heat))

        self.rw_chn2018_index_sum = rw_index_sum.copy()
        self.radwaste_class_chn2018 = rw_class

    def analysis_radwaste_usnrc(self, rws=None):
        """
        Analysis the radwaste classification.

        Parameters:
        -----------
        rws: RadwasteStandard
            Supported standards is: USNRC.
        """

        # init rw_index with shape of (INTV, NUC, class)
        rw_index_sl = np.zeros(shape=(len(self.act),
                                      len(self.act[0]), len(rws.classes)), dtype=float)
        rw_index_ll = np.zeros(shape=(len(self.act),
                                      len(self.act[0]), len(rws.classes)), dtype=float)

        # calculate radwaste index for each nuclide
        for nid, nuc in enumerate(self.nuclide):
            # get the limits for the nuclide
            limits = rws.get_nuc_limits(nuc=nuc, half_life=self.half_life[nid],
                                        density=self.density)
            # loop over the interval
            for intv in range(len(self.act)):
                # calculate the index for each class
                if nuc in ('Pu241', 'Cm242') or (not utils.is_short_live(self.half_life[nid])):
                    rw_index_ll[intv, nid, :] = np.divide(
                        self.act[intv, nid], limits)
                else:
                    rw_index_sl[intv, nid, :] = np.divide(
                        self.act[intv, nid], limits)

        rw_usnrc_index_sum_ll = np.sum(rw_index_ll, axis=1)
        rw_usnrc_index_sum_sl = np.sum(rw_index_sl, axis=1)

        # claculate the clearance index for each nuclide
        ci_usnrc = np.zeros(
            shape=(len(self.act), len(self.act[0])), dtype=float)
        for nid, nuc in enumerate(self.nuclide):
            # get the ci limit for the nuclide
            limit = rws.get_nuc_limit_usnrc_clearance(nuc=nuc)
            for intv in range(len(self.act)):
                ci_usnrc[intv, nid] = self.act[intv, nid] / limit
        total_ci_usnrc = np.sum(ci_usnrc, axis=1)

        # get the radwaste classification according to the indices for each class
        rw_class = []
        for intv in range(len(self.act)):
            # USNRC use rw_usnrc_index_sum_sl and rw_usnrc_index_sum_ll to calssify radwaste
            rw_cls = rws.determine_class_usnrc(rw_usnrc_index_sum_ll[intv],
                                               rw_usnrc_index_sum_sl[intv], total_ci_usnrc[intv])
            rw_class.append(rw_cls)

        self.rw_usnrc_index_sum_ll = rw_usnrc_index_sum_ll.copy()
        self.rw_usnrc_index_sum_sl = rw_usnrc_index_sum_sl.copy()
        self.ci_usnrc = ci_usnrc.copy()
        self._total_ci_usnrc = total_ci_usnrc.copy()
        self.radwaste_class_usnrc = rw_class

    def analysis_radwaste_usnrc_fetter(self, rws=None):
        """
        Analysis the radwaste classification.

        Parameters:
        -----------
        rws: RadwasteStandard
            Supported standards is: USNRC_FETTER.
        """

        # init rw_index with shape of (INTV, NUC, class)
        rw_index = np.zeros(shape=(len(self.act),
                                   len(self.act[0]), len(rws.classes)), dtype=float)

        # calculate radwaste index for each nuclide
        for nid, nuc in enumerate(self.nuclide):
            # get the limits for the nuclide
            limits = rws.get_nuc_limits(nuc=nuc, half_life=self.half_life[nid],
                                        density=self.density)
            # loop over the interval
            for intv in range(len(self.act)):
                # calculate the index for each class
                rw_index[intv, nid, :] = np.divide(self.act[intv, nid], limits)

        rw_index_sum = np.sum(rw_index, axis=1)

        # claculate the clearance index for each nuclide
        ci_usnrc = np.zeros(
            shape=(len(self.act), len(self.act[0])), dtype=float)
        for nid, nuc in enumerate(self.nuclide):
            # get the ci limit for the nuclide
            limit = rws.get_nuc_limit_usnrc_clearance(nuc=nuc)
            for intv in range(len(self.act)):
                ci_usnrc[intv, nid] = self.act[intv, nid] / limit
        total_ci_usnrc = np.sum(ci_usnrc, axis=1)

        # get the radwaste classification according to the indices for each class
        rw_class = []
        for intv in range(len(self.act)):
            # USNRC use rw_usnrc_index_sum_sl and rw_usnrc_index_sum_ll to calssify radwaste
            rw_cls = rws.determine_class_usnrc_fetter(
                rw_index_sum[intv], total_ci_usnrc[intv])
            rw_class.append(rw_cls)

        self.rw_usnrc_fetter_index_sum = rw_index_sum.copy()
        self.ci_usnrc = ci_usnrc.copy()
        self._total_ci_usnrc = total_ci_usnrc.copy()
        self.radwaste_class_usnrc_fetter = rw_class

    def analysis_radwaste_uk(self, rws=None):
        """
        Analysis the radwaste classification.

        Parameters:
        -----------
        rws: RadwasteStandard
            The standard used, must be UK.
        """

        # get the radwaste classification according to the:
        # alpha activity, activity and decay heat
        rw_class = []
        for intv in range(len(self.total_act)):
            # convert decay heat from kW/kg to kW/m3
            decay_heat = self.total_decay_heat[intv]  # kW/kg
            decay_heat = decay_heat * self.density * 1000.0  # kW/m3
            rw_class.append(rws.determine_class_uk(self.total_alpha_act[intv],
                                                   self.total_act[intv], decay_heat, self.total_ci[intv]))
        self.radwaste_class_uk = rw_class

    def analysis_radwaste_russian(self, rws=None):
        """
        Analysis the radwaste classification.

        Parameters:
        -----------
        rws: RadwasteStandard
            The standard used, must be RUSSIAN.
        """

        # init rw_index with shape of (INTV, NUC, class)
        rw_index = np.zeros(shape=(len(self.act),
                                   len(self.act[0]), 1), dtype=float)

        # calculate radwaste index for each nuclide
        for nid, nuc in enumerate(self.nuclide):
            # get the limits for the nuclide
            limits = rws.get_nuc_limits(nuc=nuc)
            # loop over the interval
            for intv in range(len(self.act)):
                # calculate the index for each class
                rw_index[intv, nid, :] = np.divide(self.act[intv, nid], limits)

        # sum up the index for each nuclide, shape=(INTV, class)
        rw_index_sum = np.sum(rw_index, axis=1)

        # get the radwaste classification according to the indices for each class
        rw_class = []
        for intv in range(len(self.act)):
            rw_class.append(rws.determine_class_russian(rw_index_sum[intv]))
        self.rw_russian_index_sum = rw_index_sum.copy()
        self.radwaste_class_russian = rw_class

    def __str__(self):
        """print mcnp style cell card"""
        s = ''.join([str(self.id), '     ', str(self.mat.id),
                    ' ', '-', str(self.mat.density)])
        indent_length = len(s)
        for key, value in self.geom:
            if key == 'intersection':
                bool_mark = ''
            elif key == 'union':
                bool_mark = ':'
            elif key == 'complement':
                bool_mark = '#'
            for j, hs in enumerate(value):
                if hs.sense == '-':
                    hs_sense_str = hs.sense
                else:
                    hs_sense_str = ''
                hs_str = ''.join([bool_mark, hs_sense_str, str(hs.surf.id)])
                s = utils.mcnp_style_str_append(s, hs_str, indent_length)
        s = utils.mcnp_style_str_append(
            s, ''.join(['imp:n=', str(self.imp_n)]))
        if self.imp_p is not None:
            s = utils.mcnp_style_str_append(
                s, ''.join(['imp:p=', str(self.imp_p)]))
        return s


def _pick_max_ind_from_tuple(nid):
    '''
    Pick up the index of max row.
    The nid is a tuple returned from np.where
    such as: ([1]), ([1, 2], )
    '''
    if len(nid[0]) == 1:
        nid = int(nid[0])
    else:
        if len(nid[0]) > 1:  # in case that two nuclide have same max act
            nid = int(nid[0][0])
    return nid


def get_cell_index(cells, cid):
    """get_cell_index, get the cell index in the cells according to the id"""
    cidx = -1
    for i in range(len(cells)):
        if cells[i].id == cid:
            cidx = i
            break
    # check value
    if cidx == -1:  # this means no cell found
        raise ValueError('cell not found!')
    return cidx


def get_cell_index_by_mid(cells, mid):
    """
    Find the first cell with specific mid.
    """
    cidx = -1
    for i in range(len(cells)):
        if cells[i].mid == mid:
            cidx = i
            break
    # check value
    if cidx == -1:  # no cell found
        raise ValueError(f"cell not found for material {mid}")
    return cidx


def is_item_cell(item, cells=None):
    """
    Check whether the item means a cell.
    The item can be converted to a int number existing in Cells list.

    Parameters:
    -----------
    item : int or str
    """
    if isinstance(item, str):
        try:
            cid = int(item)
        except:  # can not convert to int
            return False
    elif isinstance(item, int):
        cid = item
    else:  # wrong type
        return False

    if cells is None:
        return True
    else:  # check whether item in cell list if cells provided
        try:
            cidx = get_cell_index(cells, cid)
            return True
        except:
            return False
