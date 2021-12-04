from decimal import *
from random import uniform
from math import e

getcontext().prec = 25
getcontext().Emax = 2000
getcontext().Emin = -2000
getcontext().traps[Overflow] = False


class endlayer:
    def __init__(self, activation, costcal=None):
        self.activationtype = activation
        if activation == "sig":
            self.activation = lambda x: 1 / (1 + Decimal(e) ** Decimal(-x))
        elif activation == "lin":
            self.activation = lambda x: Decimal(x)
        elif activation == "relu":
            self.activation = lambda x: Decimal(x) if x > 0 else 0
        elif activation == "softmax":
            self.activation = lambda x, total: Decimal(e) ** Decimal(x) / sum([Decimal(e) ** Decimal(i) for i in total])
        self.type = "endlayer"
        self.costcal = costcal

    def out(self, inputs, trueval):
        if self.activationtype != "softmax":
            self.outs = [self.activation(Decimal(i)) for i in inputs]
        else:
            self.outs = [self.activation(Decimal(i), inputs) for i in inputs]
        if self.costcal is None:
            self.cost = [(self.outs[i] - Decimal(trueval[i])) / len(self.outs) for i in range(len(self.outs))]
        else:
            self.cost = [(self.costcal(self.outs[i], Decimal(trueval[i]))) / len(self.outs) for i in
                         range(len(self.outs))]
        if self.activationtype == "sig":
            self.cost = [float(self.cost[i]) * e ** float(self.outs[i]) / (e ** float(self.outs[i]) + 1) ** 2 for i in
                         range(len(self.outs))]
        elif self.activationtype == "relu":
            self.cost = [float(self.cost[i]) if self.outs[i] > 0 else 0 for i in range(len(self.outs))]
        return self.outs, self.cost

    def pred(self, inputs):
        if self.activationtype != "softmax":
            self.outs = [self.activation(Decimal(i)) for i in inputs]
        else:
            self.outs = [self.activation(Decimal(i), inputs) for i in inputs]
        return self.outs


class twoDtooneD:
    def __init__(self, dimesions):
        self.dimenions = dimesions
        self.type = "transformer"

    def changeoneD(self, array):
        translatedarray = []
        for i in range(self.dimesions[1]):
            for t in range(self.dimenions[0]):
                translatedarray.append(array[i][t])
        return translatedarray

    def changetwoD(self, array):
        translatedarray = [[] for _ in range(self.dimenions[1])]
        for i in range(len(array)):
            translatedarray[i // self.dimenions[i]].append()
        return translatedarray


class dropout:
    def __init__(self, inputsize, dropoutchance=0.05):
        self.inputsize = inputsize
        self.dropoutchance = dropoutchance
        self.type = "dropout"

    def drop(self, input):
        for i in range(len(input)):
            if uniform(0, 1) <= self.dropoutchance:
                input[i] = 0
        return input
