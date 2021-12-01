# SPDX-FileCopyrightText: 2020 G2Elab / MAGE
#
# SPDX-License-Identifier: Apache-2.0

from autograd import make_jvp, jacobian as autograd_jac
import autograd.numpy as np
from noload.optimization.specifications import Spec
from noload.optimization.iterationHandler import Iterations
from noload.optimization.Tools import *
from noload.optimization.ExportToXML import resultsToXML

'''Used to store results'''
class Results:
    """
    objectives  = list : objective values
    eq_cstr = class StructList : equality constraints values
    ineq_cstr = class StructList : inequality constraints values
    """
    objectives  = []  #valeurs des objectifs
    eq_cstr: StructList = None  # valeurs des contraintes d'équalité
    ineq_cstr: StructList = None  # valeurs des contraintes d'inégalités
    def __init__(self, results, shape, spec:Spec, jac):
        self.jac = jac # si le résultat est un calcul de jacobien ou non
        results = StructList(results, 'flattened', shape) # les résultats
        # sont sous la forme "aplatie" (fobjectif + contraintes)
        results1 = results.unflatten() # on remet les résultats sous forme
        # "normale" pour pouvoir après les exploiter
        t1 = len(spec.objectives) # nombre de fonctions objectives
        t2 = len(spec.eq_cstr) # nombre de contraintes d'égalité
        t3 = len(spec.ineq_cstr) # nombre de contraintes d'inégalité
        self.objectives = np.array(results1[:t1]) # les t1 premiers éléments
        # de results1 sont les fonctions objectives
        sh = np.shape(self.objectives) # taille des fonctions objectives
        if (t1 == 1) and len(sh) > 1 and sh[0] == 1:
            self.objectives = self.objectives[0]
        if t2 != 0: # s'il y a au moins une contrainte d'égalité
            self.eq_cstr = StructList(results1[t1:t1 + t2]) # les éléments
            # allant de t1 à t1+t2 sont les contraintes d'égalité
            sh = self.eq_cstr.shape # taille des contraintes d'égalité
            if (t2 == 1) and len(sh) > 1 and sh[0] == 1:
                self.eq_cstr.List = self.eq_cstr.List[0]
        if t3 != 0: # s'il y a au moins une contrainte d'inégalité
            self.ineq_cstr = StructList(results1[-t3:]) # les t3 derniers
            # éléments sont les contraintes d'inégalité
            sh = self.ineq_cstr.shape # taille des contraintes d'inégalité
            if (t3 == 1) and len(sh) > 1 and sh[0] == 1:
                self.ineq_cstr.List = self.ineq_cstr.List[0]

        # if t2 != 0:
        #     self.eq_cstr    = self.normalizeEq(results[t1:t1+t2],
        #     spec.eq_cstr_val)
        # if t3 != 0:
        #     self.ineq_cstr  = self.normalizeIneq(results[-t3:],
        #     spec.ineq_cstr_bnd)

    def normalizeEq(self, values, limits):
        """
        Puts the values of equality constraints between the limits
        given in inputs.
        :param values: values wished for the equality constraints
        :param limits: limits wished for the equality constraints
        :return: the values normalized of the equality constraints
        """
        # if limits!=0:
        #     results = (values.T  / limits).T
        # else:
        results = values
        for i in range(len(limits)):
            if limits[i] != 0:
                results[i] = values[i] / limits[i]
        return results
    def normalizeIneq(self, values, bounds):
        """
        Puts the values of inequality constraints between the limits
        given in inputs.
        :param values: values wished for the inequality constraints
        :param limits: limits wished for the inequality constraints
        :return: the values normalized of the inequality constraints
        """

        min = np.array([bnd[0] for bnd in bounds])  #TODO gérer des
        # variables plus complexes comme des vecteurs d'inconnus
        max = np.array([bnd[1] for bnd in bounds])
        # min = bounds[0]
        # max = bounds[1]
        if (self.jac):
            results = values
        else:
            results = ((values.T - min).T).T    #TODO gerer les None
        results = (results.T / (abs(max-min))).T
        return results

class Wrapper:
    """
    model = None : function of the model where we compute the objective
    and constraint functions
    p = dict : constant parameters of the model (optional)
    spec = class Spec : desired performances (objective functions, constraints)
    resultsHandler = list : allows to save the results as they come in
    (optional)
    constraints = list : vector of inequality constraints to be filled at
    each iteration
    xold = list : vector x "old" (not updated) for function evaluations
    xold_g = list : "old" x-vector (not updated) for gradient calculations
    results_val = class Results :values of objectives and constraints
    results_grad = class Results : gradients of objectives and constraints
    rawResults = dict : values of the model outputs
    resultsShape = list : shape of output vector (it "flattens" the results)
    """

    model  = None
    p      = None
    spec : Spec  = None
    resultsHandler = None
    constraints = []
    xold   = None
    xold_g = None
    results_val : Results = None #valeurs des objectifs et contraintes
    results_grad : Results = None #gradients des objectifs et contraintes
    rawResults   = None #valeurs des sorties du model
    resultsShape = None #forme du vecteur de sortie (mise à plat des résultats
    # pour autograd)

    def __init__(self, model : 'function to compute',
                 specifications : Spec ,
                 parameters : 'a List of inputs that are not optimized' = [],
                 resultsHandler : "for real time plotting for instance" = None):
        self.model = model
        self.p = parameters
        self.spec = specifications
        # permet de sauvegarder les résultats au fur et à mesure (optionnel)
        if resultsHandler==True:
            self.resultsHandler = Iterations(specifications.iNames,
                                             specifications.oNames,
                                             specifications.freeOutputs)
#        elif resultsHandler != None:
#            self.resultsHandler = resultsHandler
        #else : no resultHandler => no iteration history

        self.init()

    def init(self):
        self.constraints=[]
        if len(self.spec.eq_cstr) != 0:
            self.constraints.append({'type': 'eq',
                 'fun' : self.eq_cstr_val,
                 'jac' : self.eq_cstr_grad})
        if len(self.spec.ineq_cstr) != 0:
            self.constraints.append({'type': 'ineq',
                 'fun' : self.ineq_cstr_val,
                 'jac' : self.ineq_cstr_grad})
        self.xold = None
        self.xold_g = None
        self.results_val = None
        self.results_grad = None
        self.rawResults = None

    ## 3 fonctions pour récupérer les VALEURS des objectifs et contraintes
    def f_val(self, x):
        """
        Gets the value of the objective function evaluated in x according to
        the compute_model method.
        :param x: the vector of optimization variables
        :return: the value of the objective function evaluated in x
        """
        if (not np.array_equal(self.xold,x)):
            self.results_val=Results(self.compute_model(x), self.resultsShape,
                                     self.spec, jac = False)
            self.xold=np.array(x, copy=True) 
        return self.results_val.objectives

    def eq_cstr_val(self, x):
        """
        Returns the values of the equality constraints of the model evaluated
        in x according to the compute_model method.
        Handles mixed constraints (scalar + vector).
        :param x: the vector of optimization variables
        :return: returns the vector containing the subtraction between the
        equality constraints evaluated in x and the
        desired constraints given in the specifications class
        """
        if (not np.array_equal(self.xold,x)):
            self.results_val = Results(self.compute_model(x), self.resultsShape,
                                       self.spec, jac = False)
            self.xold=np.array(x, copy=True)
        #il faut bien se mettre en dehors du if car le calcul du model aura pu
        # être fait dans une autre fonction.
        if (self.spec.eq_cstr_val.List != []): # s'il y a au moins une
            # contrainte d'égalité
            self.results_val.eq_cstr.List = \
                np.array(self.results_val.eq_cstr.flatten()) - \
                np.array(self.spec.eq_cstr_val.flatten()) # -1
            # pour calculer les contraintes d'égalité, on fait la soustraction
            # entre les contraintes calculées et les spécifications désirées
            # qui sont aplaties pour gérer les contraintes complexes (scalaires
            # + vectorielles) -> pour l'algorithme, il faudra que la
            # soustraction soit nulle pour que les contraintes d'égalité soient
            # respectées
        return np.array(self.results_val.eq_cstr.List) # on renvoie les valeurs
        # des contraintes d'égalité

    def ineq_cstr_val(self, x):
        """
        Returns the values of the different inequality constraints of the model
        evaluated in x according to the compute_model method.
        Handles mixed constraints (scalar + vector).
        :param x: the vector of optimization variables
        :return: returns the vector containing the subtraction between the
        inequality constraints evaluated in x and the
        desired constraints given in the specifications class
        """
        if (not np.array_equal(self.xold,x)):
            res=self.compute_model(x)
            self.results_val = Results(res, self.resultsShape, self.spec,
                                       jac = False)
            self.xold=np.array(x, copy=True)
        constraints=self.results_val.ineq_cstr.List
        if (self.spec.ineq_cstr_bnd.List != []):  # s'il y a au moins une
            # contrainte d'inégalité
            constraints = [] # on initialise le vecteur constraints
            for i, cstr in enumerate(self.spec.ineq_cstr_bnd.List): # on fait
                # la liste de toutes les différentes contraintes
                # d'inégalité (scalaires et vectorielles) et de leurs positions
                # dans le vecteur "specifications"
                if isinstance(cstr[0], (int, float)) or cstr[0]==None \
                        or cstr[1]==None: # si la contrainte est scalaire
                    if (cstr[0] != None): # s'il y a une borne inf
                        constraints.append(self.results_val.ineq_cstr.List[i]
                                           - cstr[0])  # borne inf = 0 après
                        # normalisation
                        # on ajoute au vecteur constraints la soustraction entre
                        # la valeur de la contrainte d'inégalité obtenue et
                        # la borne inf
                        if (cstr[1] != None):  # s'il y a une borne sup en plus
                            constraints.append(cstr[1] -
                                            self.results_val.ineq_cstr.List[i])
                            # sup = 1 si normalisé
                            # on ajoute au vecteur constraints la soustraction
                            # entre la borne sup et la valeur de la
                            # contrainte d'inégalité obtenue
                    else:  # on suppose que sup est différent de None ! Par
                        # contre il n'y a pas de borne inf
                        constraints.append(cstr[1] -
                                           self.results_val.ineq_cstr.List[i])
                        # sup = 1 si normalisé
                        # on ajoute au vecteur constraints la soustraction
                        # entre la borne sup et la valeur de la
                        # contrainte d'inégalité obtenue
                else: # si la contrainte est vectorielle
                    for j in range(len(cstr)): # on parcourt les différentes
                        # composantes de cette contrainte vectorielle
                        if (cstr[j][0]!= None): # s'il y a une borne inf
                            constraints.append(
                                self.results_val.ineq_cstr.List[i][j] -
                                cstr[j][0])  # borne inf = 0 après normalisation
                            # on ajoute au vecteur constraints la soustraction
                            # entre la valeur de la contrainte d'inégalité
                            # obtenue et la borne inf
                            if (cstr[j][1] != None):  # s'il y a une borne sup
                                # en plus
                                constraints.append(cstr[j][1] -
                                        self.results_val.ineq_cstr.List[i][j])
                                # sup = 1 si normalisé
                                # on ajoute au vecteur constraints la
                                # soustraction entre la borne sup et la valeur
                                # de la contrainte d'inégalité obtenue
                        else:  # on suppose que sup est différent de None !
                            # Par contre il n'y a pas de borne inf
                            constraints.append(cstr[j][1] -
                                self.results_val.ineq_cstr.List[i][j])
                            # sup = 1 si normalisé
                            # on ajoute au vecteur constraints la soustraction
                            # entre la borne sup et la valeur de la
                            # contrainte d'inégalité obtenue
        return np.array(constraints) # on renvoie les valeurs des contraintes
        # d'inégalité

    ## 3 fonctions pour récupérer les GRADIENTS des objectifs et contraintes
    def f_grad(self, x):
        """
        Returns the gradient of the objective function evaluated in x according
        to the Jacobian of the compute_model method. (reverse mode)
        :param x: the vector of optimization variables
        :return: the gradient of the objective function evaluated in x
        """
        if (not np.array_equal(self.xold_g,x)):
            grad = autograd_jac(self.compute_model)(x)
            self.results_grad = Results(grad, self.resultsShape, self.spec,
                                        jac = True)
            self.xold_g=np.array(x, copy=True)
        return self.results_grad.objectives
    # Autre methode de calcul du Jacobien, à utiliser si il la dimension en
    # sortie est plus grande qu'en entrée
    def f_grad_using_make_jvp(self, x):
        """
        Returns the gradient of the objective function evaluated in x according
        to the Jacobian of the compute_model method. (forward mode)
        :param x: the vector of optimization variables
        :return: the gradient of the objective function evaluated in x
        """
        if (not np.array_equal(self.xold_g, x)):
            a = np.array([1])
            basis = np.pad(a, [(0, len(x) - 1)], mode='constant')  # create
            # first vector basis (1, 0, 0, ...)
            val_of_f, jac = (make_jvp(self.compute_model)(x))(basis)
            lines=len(jac)
            for i in range(1, len(x)):
                basis = np.roll(basis, 1)
                val_of_f, col_of_jacobian = \
                    (make_jvp(self.compute_model)(x))(basis)
                jac=np.append(jac, col_of_jacobian, axis = 0)
            jac =np.reshape(jac,(len(x),lines)).T
            self.results_grad = Results(jac, self.resultsShape, self.spec,
                                        jac = True)
            self.xold_g=np.array(x, copy=True)
        return self.results_grad.objectives

    def eq_cstr_grad(self, x):
        """
        Returns the gradient of the different equality constraints of the model
        evaluated in x according to the Jacobian of the compute_model method.
        Handles mixed constraints (scalar + vector).
        :param x: the vector of optimization variables
        :return: the vector of gradient equality constraints evaluated in x
        """
        if (not np.array_equal(self.xold_g,x)):
            self.results_grad = Results(autograd_jac(self.compute_model)(x),
                                    self.resultsShape, self.spec, jac = True)
            self.xold_g=np.array(x, copy=True)
        if self.spec.eq_cstr_val.List==[]:
            return self.results_grad.eq_cstr.List
        res = [] # on va aplatir les gradients des contraintes complexes
        # (scalaires + vectorielles)
        for i in range(len(self.results_grad.eq_cstr.List)): # on parcourt
            # le résultat obtenu (gradient de contraintes d'égalité)
            if isinstance(self.spec.eq_cstr_val.List[i],(int,float)): # si la
                # contrainte est scalaire
                res.append(self.results_grad.eq_cstr.List[i]) # on ajoute
                # simplement son gradient dans la nouvelle liste res
            elif isinstance(self.spec.eq_cstr_val.List[i], list): # si la
                # contrainte est vectorielle
                for j in range(len(self.results_grad.eq_cstr.List[i])): # on
                    # parcourt chaque élément de son gradient
                    res.append(self.results_grad.eq_cstr.List[i][j]) # on les
                    # ajoute un par un à la liste res
        return res # on renvoie les gradients des contraintes d'égalité

    def ineq_cstr_grad(self, x):
        """
        Returns the gradient of the different inequality constraints of the
        model evaluated in x according to the Jacobian of the compute_model
        method.
        Handles mixed constraints (scalar + vector).
        :param x: the vector of optimization variables
        :return:  the vector of gradient inequality constraints evaluated in x
        """
        if (not np.array_equal(self.xold_g,x)):
            self.results_grad = Results(autograd_jac(self.compute_model)(x),
                                    self.resultsShape, self.spec, jac = True)
            self.xold_g=np.array(x, copy=True)
        # on duplique les contraintes d'inégalité qui on une borne supérieure:
        res=self.results_grad.ineq_cstr.List
        if (self.spec.ineq_cstr_bnd.List != []): # s'il y a au moins une
            # contrainte d'inégalité
            res = [] # on initialise le vecteur res (gradients des contraintes
            # d'inégalité)
            for i, cstr in enumerate(self.spec.ineq_cstr_bnd.List): # on fait
                # la liste de toutes les différentes contraintes
                # d'inégalité (scalaires et vectorielles) et de leurs positions
                # dans le vecteur "specifications"
                if isinstance(cstr[0], (int, float)) or cstr[0]==None: # si la
                    # contrainte est scalaire
                    if (cstr[0] != None): # s'il y a une borne inf
                        res.append(self.results_grad.ineq_cstr.List[i]) # on
                        # ajoute le résultat tel quel
                        if (cstr[1] != None): # s'il y a une borne sup en plus
                            res.append(-self.results_grad.ineq_cstr.List[i])
                            # on ajoute l'opposé du résultat car par défaut
                            # SLSQP : ctr>0
                    else:  # on suppose que sup est différent de None ! Par
                        # contre il n'y a pas de borne inf
                        res.append(- self.results_grad.ineq_cstr.List[i])
                else: # si la contrainte est vectorielle
                    for j in range(len(cstr)):  # on parcourt les différentes
                        # composantes de cette contrainte vectorielle
                        if (cstr[j][0] != None):  # s'il y a une borne inf
                            res.append(np.array(
                                self.results_grad.ineq_cstr.List[i][j]))
                            # on ajoute le résultat tel quel
                            if (cstr[j][1] != None): # s'il y a une borne sup
                                # en plus
                                res.append(-np.array(
                                    self.results_grad.ineq_cstr.List[i][j]))
                                # on ajoute l'opposé du résultat car par défaut
                                # SLSQP : ctr>0
                        else:   # on suppose que sup est différent de None !
                            # Par contre il n'y a pas de borne inf
                            res.append(-np.array
                            (self.results_grad.ineq_cstr.List[i][j]))
        return res # on renvoie les gradients des contraintes d'inégalité

    # fonction utilisée par minimize de scipy
    def f_val_grad(self, x):
        """
        Function used by scipy minimize.
        :param x: the vector of optimization variables
        :return: a tuple including the evaluation of the objective function
        evaluated in x and its gradient
        """
        return (self.f_val(x), self.f_grad(x))

    # wrapper permettant d'être selectif sur les sorties du modèles,
    # en particulier pour le calcul du Jacobien
    def compute_model(self, x):
        """
        Computes the model outputs (objective function + constraints) in x. 
        Stores the results (optimization variables + model outputs) got at
        each iteration.
        :param x: the vector of optimization variables
        :return: returns a "flattened" vector out including the model outputs
        """
        if len(self.spec.iNames)==1 and len(x)!=1:   #TODO, patch for 1 array
            # variable, to do more general
            xList = dict(zip(self.spec.iNames, [x]))
        elif self.spec.xinit_sh != [0] * len(self.spec.iNames) \
                and self.spec.xinit_sh!=[]:
            var = StructList(x, 'flattened', self.spec.xinit_sh)
            xList = dict(zip(self.spec.iNames, var.unflatten()))
        else:
            xList = dict(zip(self.spec.iNames, x))  #TODO, verifier que ça
            # fonctionne pour une liste d'entrée scalaire et vectorielle
            # (uniquement le premier élement du vecteur ?)
        if self.p != []:
            res = self.model(**xList, **self.p)
        else:
            res = self.model(**xList)
        dico = {k: v for k, v in res.__iter__()}  # conversion en dictionnaire
        out = [dico[vars] for vars in self.spec.oNames]     #TODO attraper
        # une exception si la variable du cahier des charge n'appartient pas
        # aux sorties du modèle
        #TODO l'agregation des sortie pose un pb pour les sortie vectorielle
        # (par exemple pour l'optimi Leastsqare)
        # sauvegarde et tracé des résultats uniquement si appel à la fonction
        # et non au gradient
        for i in range(len(out)):
            if (type(out[i]) == np.numpy_boxes.ArrayBox):
                if (type(out[i]._value)==np.ndarray):
                    out[i]=list(out[i])
        if (type(x[0]) != np.numpy_boxes.ArrayBox):
            self.rawResults = dico
            if self.spec.freeOutputs !=[]:
                fData= [dico[vars] for vars in self.spec.freeOutputs]
            else:
                fData=[]
            if (self.resultsHandler!=None):
                if self.spec.xinit_sh != [0] * len(self.spec.iNames):
                    var = StructList(x, 'flattened', self.spec.xinit_sh)
                    self.resultsHandler.updateData(var.unflatten(), out,fData)
                else:
                    self.resultsHandler.updateData(x, out,fData)
        out = StructList(out) # on récupère les sorties du modèle
        self.resultsShape = out.shape
        out2 = out.flatten() # on aplatit les sorties du modèle
        return np.array(out2) # renvoie la sortie sous forme de jax.numpy array


    def solution(self):
        """
        Returns the model inputs computed at the last iteration of the
        algorithm.
        :return: list of model inputs
        """
        if self.spec.xinit_sh != [0] * len(self.spec.iNames):
            return self.resultsHandler.solutions[-1].iData
        return self.resultsHandler.solutions[-1].iData.tolist()

    def getLastInputs(self):
        """
        Returns the model inputs computed at the last iteration of the
        algorithm.
        :return: dictionary containing the model inputs
        """
        lastSol = self.resultsHandler.solutions[-1]
        if len(self.resultsHandler.iNames)==1:
            dico = {self.resultsHandler.iNames[0]:
                        np.array(lastSol.iData).tolist()}
        else:
            dico = {self.resultsHandler.iNames[i]: lastSol.iData[i]
                    for i in range(len(self.resultsHandler.iNames))}
        return dico

    def getLastOutputs(self):
        """
        Returns the outputs of the model computed at the last iteration of
        the algorithm.
        :return: dictionary containing the model outputs
        """
        lastSol = self.resultsHandler.solutions[-1]
        dico = {self.resultsHandler.oNames[i]: lastSol.oData[i]
                for i in range(len(self.resultsHandler.oNames))}
        if self.spec.freeOutputs !=[]:
            dico.update({self.resultsHandler.fNames[i]: lastSol.fData[i]
                         for i in range(len(self.resultsHandler.fNames))})
        return dico

    def printResults(self):
        """
        Displays the inputs and outputs of the model computed at the last
        iteration of the algorithm.
        :return: /
        """
        print(self.getLastInputs())
        print(self.getLastOutputs())

    def printAllResults(self):
        """
        Displays the inputs and outputs of the model computed at each iteration
         of the algorithm.
        :return: /
        """
        sols = self.resultsHandler.solutions
        for sol in sols:
            if len(self.resultsHandler.iNames)==1:
                dico = {self.resultsHandler.iNames[0]:
                            np.array(sol.iData).tolist()}
            else:
                dico = {self.resultsHandler.iNames[i]:
                   sol.iData[i] for i in range(len(self.resultsHandler.iNames))}
            print(dico)

    def getIteration(self,iternum):
        '''
        Returns the inputs and the outputs of the model computed at the number
        of iteration given in parameter.
        :param iternum: the number of iteration
        :return: dictionnaries containing the inputs and outputs
        '''
        sols=self.resultsHandler.solutions
        sol=sols[iternum-1]
        if len(self.resultsHandler.iNames)==1:
            iData={self.resultsHandler.iNames[0] : np.array(sol.iData).tolist()}
        else:
            iData={self.resultsHandler.iNames[i] : sol.iData[i]
                   for i in range(len(self.resultsHandler.iNames))}
        oData={self.resultsHandler.oNames[i] : sol.oData[i]
               for i in range(len(self.resultsHandler.oNames))}
        if self.spec.freeOutputs != []:
            fData={self.resultsHandler.fNames[i] : sol.fData[i]
                   for i in range(len(self.resultsHandler.fNames))}
            return iData,oData,fData
        else:
            return iData,oData

    def exportToXML(self, fileName):
        """
        Return an XMLfile compatible with CADES. This can be used to plot
        geometry in GeomMaker.
        :param fileName: the filename to save XML tree
        :return: /
        """
        return resultsToXML(self.resultsHandler, fileName)

    def plotResults(self):
        """
        Displays the results (inputs + outputs) graphically.
        :return: /
        """

        import noload.gui.plotIterations as pltIter
        pltIter.plotIO(self.resultsHandler)

    def plotNormalizedSolution(self):
        """
        Displays the "normalized" solution (values between 0 and 1) graphically.
        :return: /
        """
        bnd=np.transpose(self.spec.bounds)
        sols = self.solution()
        x = list(range(0,len(sols)))
        #normalize :
        mean = (bnd[1]+bnd[0])/2
        init = self.spec.xinit
        solsN = (sols-init)/(bnd[1]-bnd[0])

        import matplotlib.pyplot as plt
        plt.bar(x, solsN)
        plt.show()

