import time
from random import randint

layertypes = ["fullcon", "endlayer", "2Dpool", "noise", "loss", "boost", "SmartBoost"]


class network:
    def __init__(self, layers):
        self.layers = layers
        self.prevcost = []

    def runnet(self, alpha, epochs, inputs, outputs, storedata=None, regularization=None, momentum=None,
               printevery=None, batchsize=1):
        if momentum is not None:
            if not isinstance(momentum, object):
                raise RuntimeError("Variable must be a valid momentum class")
            for layer in self.layers:
                if layer.type == "fullcon":
                    layer.applymomentum(momentum)
        else:
            for layer in self.layers:
                if layer.type == "fullcon":
                    layer.applymomentum(None)
        if regularization is not None:
            totalneuron = 0
            if not isinstance(regularization, object):
                raise RuntimeError("Variable must be a valid regularization class")
            for layer in self.layers:
                if layer.type == "fullcon":
                    totalneuron += len(layer.weights[0])
            try:
                regularization = regularization.setregularization(totalneuron)
            except AttributeError:
                raise RuntimeError(f"The object is not a valid regularization layer")
        for layer in self.layers:
            if layer.type == "loss":
                alpha += alpha - layer.newrate(alpha)
        for i in range(epochs * batchsize):
            chosen = randint(0, len(inputs) - 1)
            chosenin = inputs[chosen]
            chosenout = outputs[chosen]
            for layer in self.layers:
                try:
                    try:
                        if layer.type == "fullcon":
                            chosenin = layer.forwardpass(chosenin)
                        elif layer.type == "noise":
                            chosenin = layer.noiseadd(chosenin)
                        elif layer.type == "endlayer":
                            predout, cost = layer.out(chosenin, chosenout)
                        elif layer.type == "loss":
                            alpha = layer.newrate(alpha)
                        elif layer.type == "boost":
                            alpha = layer.boost(i, alpha)
                        elif layer.type == "SmartBoost":
                            alpha = layer.boost(i, alpha, epochs)
                    except AttributeError:
                        raise RuntimeError(f"The object {layer.type} is not a valid layer")
                except AttributeError:
                    raise RuntimeError(f"The object is not a valid layer")
            if regularization is not None:
                try:
                    cost = regularization.regulise(cost)
                except AttributeError:
                    raise RuntimeError(f"The object is not a valid regularization class")
            if storedata is not None:
                try:
                    storedata.learning(alpha)
                    storedata.cost(cost)
                except AttributeError:
                    raise RuntimeError(f"The object is not a valid storedata class")
            if i != 0 and i % batchsize == 0:
                cost = [i / batchsize for i in totalcost]
                for t in range(len(self.layers) - 1, 0, -1):
                    if self.layers[t - 1].type == "fullcon":
                        try:
                            cost = self.layers[t - 1].backprop(cost, alpha)
                            self.layers[t - 1].update()
                        except AttributeError:
                            raise RuntimeError(f"The object is not a valid layer")
                totalcost = 0
            elif i == 0:
                totalcost = cost
            else:
                totalcost = cost
            if printevery is not None:
                if i % (printevery * batchsize) == 0:
                    if i != 0:
                        print(
                            f"\n\nEpoch No. {int(i / batchsize)}\nPast {printevery} epochs took: {round(time.time() - start, 3)} seconds\n Estimated time: {epochs*(round(time.time() - start, 3)/printevery)}")
                        start = time.time()
                    else:
                        print(f"\n\nCurrent epoch is: {int(i / batchsize)}")
                        start = time.time()

        if storedata is not None:
            return storedata

    def predwithout(self, inputs, outputs):
        av = [0 for _ in range(len(outputs[0]))]
        outputlist = []
        for i in range(len(inputs)):
            chosenin = inputs[i]
            chosenout = outputs[i]
            for layer in self.layers:
                if layer.type == "fullcon":
                    try:
                        chosenin = layer.forwardpass(chosenin)
                    except AttributeError:
                            raise RuntimeError(f"The object is not a valid layer")
                elif layer.type == "endlayer":
                    try:
                        predout, cost = layer.out(chosenin, chosenout)
                    except AttributeError:
                            raise RuntimeError(f"The object is not a valid layer")
                    av = [cost[i] + av[i] for i in range(len(cost))]
                    print("Input was: " + str(inputs[i]) + ", target output was: " + str(
                        outputs[i]) + ", predicted output was: " + str([float(s) for s in predout]))
                    outputlist.append([inputs[i], outputs[i], predout])
        print("Average cost was: " + str([float(i / len(inputs)) for i in av]))
        return outputlist

    def pred(self, inputs):
        outputlist = []
        for i in range(len(inputs)):
            chosenin = inputs[i]
            for layer in self.layers:
                try:
                    if layer.type == "fullcon":
                        chosenin = layer.forwardpass(chosenin)
                    elif layer.type == "endlayer":
                        predout = layer.pred(chosenin)
                        outputlist.append([inputs[i], predout])
                except AttributeError:
                        raise RuntimeError(f"The object is not a valid layer")
        return outputlist

    def applywb(self, wb):
        curwb = 0
        for layer in self.layers:
            try:
                if layer.type == "fullcon":
                    layer.loadwb(wb[curwb])
            except AttributeError:
                raise RuntimeError(f"The object is not a valid layer")
            curwb += 1

    def returnwb(self):
        wb = []
        for layer in self.layers:
            if layer.type == "fullcon":
                try:
                    wb.append(layer.returnwb())
                except AttributeError:
                    raise RuntimeError(f"The object is not a valid layer")
        return wb


def raiseinvalidlayer():
    raise RuntimeError("Layer is invalid")


def create(layers):
    return network(
        [layer if any(layer.type == name for name in layertypes) else raiseinvalidlayer() for layer in layers])
