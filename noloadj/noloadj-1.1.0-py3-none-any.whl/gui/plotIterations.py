# SPDX-FileCopyrightText: 2021 G2Elab / MAGE
#
# SPDX-License-Identifier: Apache-2.0

import matplotlib
#matplotlib.use('TkAgg')
#start all your IPython kernels in inline mode by default by setting the following config options in your config files:
#IPKernelApp.matplotlib=<CaselessStrEnum>
#  Default: None
#  Choices: ['auto', 'gtk', 'gtk3', 'inline', 'nbagg', 'notebook', 'osx', 'qt', 'qt4', 'qt5', 'tk', 'wx']
#  Configure matplotlib for interactive use with the default matplotlib backend.

import matplotlib.pyplot as plt
from typing import List
from noloadj.optimization.iterationHandler import Solution, Iterations
from noloadj.optimization.specifications import Spec

class DynamicUpdate():

    def __init__(self, spec:Spec):
        plt.ion()  # Turn the interactive mode on.
        self.spec = spec
        self.nbI=len(spec.iNames)
        self.nbO=len(spec.oNames)
        maxVarPlot = 3
        self.nbI = min(maxVarPlot, self.nbI)#TODO faire quelque chose
        # pour afficher proprement plus de 10 variables
        self.nbO = min(maxVarPlot, self.nbO)
        self.lines = [None for _ in range(self.nbI+self.nbO)]
        #Set up plot
        self.figure, self.axes = plt.subplots(self.nbI+self.nbO, 1, sharex=True)
        #TODO faire un subplot avec 2 figures pour séparer inputs and outputs
        plt.xlabel('iterations')
        for i in range(1, self.nbI+1):
            self.lines[i], = self.axes[i].plot([],[],'o')
            self.axes[i].set_ylabel(spec.iNames[i])
            #Autoscale on unknown axis and known lims on the other
            self.axes[i].set_autoscaley_on(True)
            #Other stuff
            self.axes[i].grid()
        for i in range(1, self.nbO+1):
            self.lines[self.nbI+i], = self.axes[self.nbI+i].plot([],[],'o')
            self.axes[self.nbI+i].set_ylabel(spec.oNames[i])
            #Autoscale on unknown axis and known lims on the other
            self.axes[self.nbI+i].set_autoscaley_on(True)
            #Other stuff
            self.axes[self.nbI+i].grid()

    def update(self, sol:List[Solution]):
        """
        Adds the solution given in inputs to the graph.
        :param sol: Solution to add to the graph
        :return: /
        """
        xdata = range(len(sol))
        for i in range(self.nbI):
            #Update data (with the new _and_ the old points)
            self.lines[i].set_xdata(xdata)
            self.lines[i].set_ydata([s.iData[i] for s in sol])
            #affiche les entrées
            #Need both of these in order to rescale
            self.axes[i].relim()
            self.axes[i].autoscale_view()
            #We need to draw *and* flush

        for i in range(self.nbO):
            #Update data (with the new _and_ the old points)
            self.lines[self.nbI+i].set_xdata(xdata)
            self.lines[self.nbI+i].set_ydata([s.oData[i] for s in sol])
            #affiche les sorties
            #Need both of these in order to rescale
            self.axes[self.nbI+i].relim()
            self.axes[self.nbI+i].autoscale_view()
            #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def finalize(self):
        """
        Shows the graph.
        :return: /
        """
        plt.show(block=True)

    def __del__(self):      #ça ne fonctionne pas
        plt.show(block=True)

def show():
    """
    Shows the graph.
    :return: /
    """
    plt.show(block=True)

def plotIO(iter:Iterations):
    """
    Builds a graph displaying the inputs and outputs of the model.
    :param iter: class Iterations including inputs and outputs (for each
    iteration).
    :return: /
    """
    plot("Input optimization convergence", iter.iNames,
         range(1, len(iter.solutions)+1), [sol.iData for sol in iter.solutions])
    plot("Output optimization convergence", iter.oNames,
         range(1, len(iter.solutions)+1), [sol.oData for sol in iter.solutions])
    plt.show()

def plot(title, names,x,y):
    """
    Builds a graph displaying two axes x and y.
    :param title: title of the graph
    :param names: names of axes x and y
    :param x: values on axe x
    :param y: values on axe y
    :return: /
    """
    nb=len(names)
    #Pour gérer une seule variable, mais vectorielle
    if nb==1 and len(y[0])>1 :
        nb=len(y[0])
        names = [names[0]+str(i) for i in range(1,nb)]

    maxVarPlot=5
    nb = min(maxVarPlot, nb)# TODO faire quelque chose pour afficher
    # proprement plus de 5 sorties.

    lines = [None for _ in range(nb)]
    figure, axes = plt.subplots(nb, 1, sharex=True)
    figure.suptitle(title)
    plt.xlabel('iterations')
    if nb>1 :
        for i in range(nb):
            lines[i], = axes[i].plot(x,[row[i] for row in y],'o')
            axes[i].set_ylabel(names[i])
            #Autoscale on unknown axis and known lims on the other
            axes[i].set_autoscaley_on(True)
            #Other stuff
            axes[i].grid()
    else:
        lines = axes.plot(x, [row[0] for row in y], 'o')
        axes.set_ylabel(names[0])
        # Autoscale on unknown axis and known lims on the other
        axes.set_autoscaley_on(True)
        # Other stuff
        axes.grid()

    plt.show(block=False)


def plotXY(iter:Iterations, title = "X-Y Plot"):
    """
    Builds a graph displaying the inputs and outputs of the model, of the
    form "X-Y Plot".
    :param iter: class Iterations including inputs and outputs (for each
    iteration).
    :param title: title of the graph
    :return: /
    """
    #iter.iNames, , [sol.iData for sol in iter.solutions])
    x = [sol.iData for sol in iter.solutions]
    y = [sol.oData for sol in iter.solutions]

    nb=len(iter.oNames)
    maxVarPlot=5
    nb = min(maxVarPlot, nb)# TODO faire quelque chose pour afficher proprement
    # plus de 5 sorties.
    lines = [None for _ in range(nb)]
    figure, axes = plt.subplots(nb, 1, sharex=True)
    figure.suptitle(title)
    plt.xlabel(iter.iNames[0])
    if nb>1 :
        for i in range(nb):
            lines[i], = axes[i].plot(x,[row[i] for row in y],'o-')
            axes[i].set_ylabel(iter.oNames[i])
            #Autoscale on unknown axis and known lims on the other
            axes[i].set_autoscaley_on(True)
            #Other stuff
            axes[i].grid()
    else:
        lines = axes.plot(x, [row[0] for row in y], 'o-')
        axes.set_ylabel(iter.oNames[0])
        # Autoscale on unknown axis and known lims on the other
        axes.set_autoscaley_on(True)
        # Other stuff
        axes.grid()

    plt.show()

