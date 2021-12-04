from random import random
from decimal import *
from math import e

getcontext().prec = 25
getcontext().Emax = 2000
getcontext().Emin = -2000
getcontext().traps[Overflow] = False


# noinspection PyAttributeOutsideInit
class baselayer:
    def __init__(self, activation):
        self.activationtype = activation
        if activation == "sig":
            self.activation = lambda x: 1 / (1 + Decimal(e) ** Decimal(-x))
        elif activation == "lin":
            self.activation = lambda x: Decimal(x)
        elif activation == "relu":
            self.activation = lambda x: Decimal(x) if x > 0 else 0

    def neuroncreate(self, curneur=1, nextneur=1):
        self.weights = [[random() for _ in range(nextneur)] for t in range(curneur)]
        self.biases = [0 for _ in range(nextneur)]
        self.neuroncosts = [0 for _ in range(curneur)]
        self.momentum = None

    def forwardpass(self, inputs):
        self.inputs = inputs
        try:
            if len(inputs) != len(self.weights):
                raise IndexError("Input of size " + str(len(inputs)) + " should be size " + str(len(self.weights)))
        except:
            pass
        try:
            inputs = [float(i) for i in inputs]
        except:
            raise TypeError("List must only contain int or float values")
        tempout = [0 for _ in range(len(self.weights[0]))]
        self.outs = [0 for _ in range(len(self.weights[0]))]
        for i in range(len(self.weights)):
            for t in range(len(self.weights[i])):
                tempout[t] = inputs[i] * self.weights[i][t]
            self.outs = [self.outs[s] + tempout[s] for s in range(len(tempout))]
        for i in range(len(self.outs)):
            getcontext().prec = 100
            self.outs[i] = Decimal(self.activation(float(self.outs[i]) + float(self.biases[i])))
        return self.outs

    def backprop(self, neuroncost, alpha):
        neuroncost = [float(i) for i in neuroncost]
        self.weights = [[float(i) for i in self.weights[t]] for t in range(len(self.weights))]
        self.biases = [float(i) for i in self.biases]
        if self.activationtype == "lin":
            for i in range(len(self.weights)):
                for t in range(len(self.weights[0])):
                    self.neuroncosts[i] += neuroncost[t] * self.weights[i][t] * self.inputs
        elif self.activationtype == "sig":
            for i in range(len(self.weights)):
                for t in range(len(self.weights[0])):
                    self.neuroncosts[i] += neuroncost[t] * self.weights[i][t] * e ** float(self.inputs[i]) / (
                            e ** float(self.inputs[i]) + 1) ** 2
        elif self.activationtype == "relu":
            for i in range(len(self.weights)):
                for t in range(len(self.weights[0])):
                    self.neuroncosts[i] += neuroncost[t] * self.weights[i][t] if self.inputs[i] > 0 else 0
        self.preweights = [
            [self.weights[t][i] - self.weights[t][i] * alpha * neuroncost[i] for i in range(len(neuroncost))] for t in
            range(len(self.weights))]
        self.prebiases = [self.biases[i] - self.biases[i] * alpha * neuroncost[i] for i in range(len(neuroncost))]
        if self.momentum != None:
            self.preweights = self.momentum.applymomentumw(self.preweights)
            self.prebiases = self.momentum.applymomentumb(self.prebiases)
        return self.neuroncosts

    def applymomentum(self, momentum):
        self.momentum = momentum

    def update(self):
        self.weights = self.preweights
        self.biases = self.prebiases

    def loadwb(self, wb):
        self.weights = wb[0]
        self.biases = wb[1]
        if all(not all(isinstance(t, int) or isinstance(t, float) for t in i) for i in self.weights) or not all(
                isinstance(i, int) or isinstance(i, float) for i in self.biases):
            raise RuntimeError("The weights and biases lists must only contain floats")

    def returnwb(self):
        return [self.weights, self.biases]


class denselayer(baselayer):
    def __init__(self, activation, curneur=1, nextneur=1):
        super().__init__(activation)
        super().neuroncreate(curneur, nextneur)
        self.type = "fullcon"


class twoDpoolinglayer:
    def __init__(self, activation, poolingdimesions=[2, 2]):
        self.momentum = None
        self.activationtype = activation
        if activation == "sig":
            self.activation = lambda x: 1 / (1 + Decimal(e) ** Decimal(-x))
        elif activation == "lin":
            self.activation = lambda x: Decimal(x)
        elif activation == "relu":
            self.activation = lambda x: Decimal(x) if x > 0 else 0
        self.poolingdimensions = poolingdimesions
        self.weights = [[random() for _ in range(poolingdimesions[0])] for _ in range(poolingdimesions[1])]
        self.type = "2Dpool"

    def forwardpass(self, inputs):
        try:
            inputs = [[Decimal(t) for t in i] for i in inputs]
            self.inputs = inputs
            output = []
            for i in range(len(inputs) - self.poolingdimensions[1] + 1):
                xout = []
                for t in range(len(inputs[0]) - self.poolingdimensions[0] + 1):
                    total = 0
                    for y in range(self.poolingdimensions[1]):
                        for x in range(self.poolingdimensions[0]):
                            total += inputs[i + y][t + x] * Decimal(self.weights[y][x])
                    xout.append(self.activation(total))
                output.append(xout)
        except:
            raise RuntimeError("Inputs are not of an even shape or not large enough for pooling dimensions")
        self.outputs = output
        return output

    def backprop(self, neuroncost, alpha):
        self.preweightchange = [[0 for _ in range(self.poolingdimesions[0])] for _ in range(self.poolingdimesions[1])]
        self.neuroncost = [[0 for _ in range(neuroncost[0] + self.poolingdimensions[0])] for _ in
                           range(self.poolingdimensions[1])]
        for i in range(len(neuroncost)):
            for t in range(len(neuroncost[0])):
                for y in range(self.poolingdimensions[1]):
                    for x in range(self.poolingdimensions[0]):
                        temp = 0
                        if self.activationtype == "lin":
                            temp += Decimal(self.weights[y][x]) * neuroncost[i][t] * self.inputs[i][t]
                        elif self.activationtype == "sig":
                            temp += Decimal(self.weights[y][x]) * neuroncost[i][t] * e ** float(self.inputs[i][t]) / (
                                    e ** float(self.inputs[i][t]) + 1) ** 2
                        elif self.activationtype == "relu":
                            temp += Decimal(self.weights[y][x]) * neuroncost[i][t] if self.inputs[i][t] > 0 else 0
                        self.neuroncost[i + y][t + x] += temp
                        self.preweightchange[y][x] += temp

    def update(self):
        self.weights = [[self.weights[i][t] + self.preweightchange[i][t] for t in range(self.poolingdimensions[0])] for
                        i in range(self.poolingdimensions[1])]
