# SPDX-FileCopyrightText: 2020 G2Elab / MAGE
#
# SPDX-License-Identifier: Apache-2.0

import autograd.numpy as np
from autograd.builtins import isinstance
from noload.optimization.Tools import *
'''Define optimization specification including objectives and constraints'''
class Spec:
    """
    iNames = list including names of optimization variables
    bounds = list including range of values of optimization variables
    xinit = list including initial values of the optimization variables
    xinit_sh = list including shape of the optimization variables
    objectives = list including names of objective functions
    eq_cstr = list including names of equality constraints
    eq_cstr_val : class StructList including values of equality constraints
    ineq_cstr = list including names of inequality constraints
    ineq_cstr_bnd : class StructList including bounds of inequality constraints
    freeOutputs = list of outputs to monitor
    nb = int number of  output variables (objective functions + constraints)
    oNames = list including names of output variables
    """

    iNames      = []  #noms des variables d'optimisation
    bounds      = []  #domaine de recherche
    xinit       = []  #valeurs initiales
    xinit_sh    = []
    objectives  = []  #noms des objectifs
    eq_cstr     = []  #noms des contraintes d'équalité
    eq_cstr_val : StructList = None  #valeurs des contraintes d'égalité
    ineq_cstr   = []  #noms des contraintes d'inégalité
    ineq_cstr_bnd : StructList = None  # domaine des contraintes d'inégalité
    freeOutputs = []  # list of outputs to monitor
    nb          = 0
    oNames       = []
    def __init__(self, variables, bounds, objectives, eq_cstr=[],
                 eq_cstr_val=[], ineq_cstr=[], ineq_cstr_bnd=[],
                 freeOutputs=[], xinit=[]):
        if isinstance(variables,dict):
            self.iNames=list(variables.keys())
            xinit=list(variables.values())
            bounds=list(bounds.values())
        elif isinstance(variables,(list,np.ndarray)):
            self.iNames=variables
        if isinstance(eq_cstr,dict):
            self.eq_cstr=list(eq_cstr.keys())
            self.eq_cstr_val=StructList(list(eq_cstr.values()))
        elif isinstance(eq_cstr, (list,np.ndarray)):
            self.eq_cstr = eq_cstr
            self.eq_cstr_val = StructList(eq_cstr_val)
        if isinstance(ineq_cstr,dict):
            self.ineq_cstr=list(ineq_cstr.keys())
            self.ineq_cstr_bnd=StructList(list(ineq_cstr.values()))
        elif isinstance(ineq_cstr,(list,np.ndarray)):
            self.ineq_cstr = ineq_cstr
            self.ineq_cstr_bnd = StructList(ineq_cstr_bnd)
        x0 = StructList(xinit)
        self.xinit_sh = x0.shape
        if self.xinit_sh != [0] * len(x0.List) or bounds!=[]:
            bnds = bounds
            bounds = []
            for i in range(len(bnds)):
                if isinstance(bnds[i][0], list):
                    for j in range(len(bnds[i])):
                        bounds.append(bnds[i][j])
                else:
                    bounds.append(bnds[i])
            x0 = StructList(xinit)
            xinit = x0.flatten()
        if not isinstance(bounds, np.ndarray):
            bounds = np.array(bounds)
        self.bounds = bounds
        if not isinstance(xinit, np.ndarray):
            xinit = np.array(xinit)
        self.xinit = xinit
        self.objectives = objectives
        self.freeOutputs = freeOutputs
        self.computeAttributes()

    def computeAttributes(self):
        """
        Concatenates the output names of the model in the list oNames.
        Computes the length of oNames in the integer nb.
        :return: /
        """
        self.oNames = np.concatenate((self.objectives, self.eq_cstr,
                                      self.ineq_cstr), axis=0)
        self.nb = len(self.oNames)

    def removeObjective(self, fobj):
        """
        Removes a function from the objectives of the model.
        Calls the computeAttributes function.
        :param fobj: the objective function to remove
        :return: /
        """
        self.objectives.remove(fobj)
        self.computeAttributes()

    def insertObjective(self, position, fobj):
        """
        Adds a function to the objectives of the model.
        Calls the computeAttributes function.
        :param position: the index where to add the objective function in the
        "objectives" list
        :param fobj: the objective function to add
        :return: /
        """
        self.objectives.insert(position, fobj)
        self.computeAttributes()

    def appendConstraint(self, cstr, value):
        """
        Adds an equality constraint.
        Calls the computeAttributes function.
        :param cstr: equality constraint to add
        :param value: the desired value of the equality constraint
        :return: /
        """
        self.eq_cstr.append(cstr)
        self.eq_cstr_val.List.append(value)
        self.computeAttributes()

    def removeLastEqConstraint(self):
        """
        Removes the last equality constraint from the model.
        Calls the computeAttributes function.
        :return: /
        """
        self.eq_cstr.pop()
        self.eq_cstr_val.List.pop()
        self.computeAttributes()


