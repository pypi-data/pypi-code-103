import time
from random import randint
layertypes = ["fullcon", "endlayer", "2Dpool", "noise", "loss", "boost", "smartboost"]

class network:
    def __init__(self, layers):
        self.layers = layers
        self.prevcost = []
    def runnet(self, alpha, epochs, inputs, outputs, storedata=None, regularization=None, momentum=None, printevery=None, batchsize=1):
        if momentum != None:
            if not isinstance(momentum, object):
                raise RuntimeError("Variable must be of the momentum class")
            for layer in self.layers:
                if layer.type == "fullcon":
                    layer.applymomentum(momentum)
        else:
           for layer in self.layers:
                if layer.type == "fullcon":
                    layer.applymomentum(None)
        if regularization != None:
            totalneuron = 0
            if not isinstance(regularization, object):
                raise RuntimeError("Variable must be of the regularization class")
            for layer in self.layers:
                if layer.type == "fullcon":
                    totalneuron += len(layer.weights[0])
            regularization = regularization.setregularization(totalneuron)
        for layer in self.layers:
            if layer.type == "loss":
                alpha += alpha - layer.newrate(alpha)
        for i in range(epochs * batchsize):
            chosen = randint(0, len(inputs)-1)
            chosenin = inputs[chosen]
            chosenout = outputs[chosen]
            for layer in self.layers:
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
                elif layer.type == "smartboost":
                    alpha = layer.boost(i, alpha, epochs)
            if regularization != None:
                cost = regularization.regulise(cost)
            if storedata != None:
                storedata.learning(alpha)
                storedata.cost(cost)
            if i != 0 and i % batchsize == 0:
                cost = [i / batchsize for i in totalcost]
                for t in range(len(self.layers)-1, 0, -1):
                    if self.layers[t-1].type == "fullcon":
                        cost = self.layers[t-1].backprop(cost, alpha)
                        self.layers[t-1].update()
                totalcost = 0
            elif i == 0:
                totalcost = cost
            else:
                totalcost = cost
            if printevery != None:
                if i % (printevery * batchsize) == 0:
                    if i != 0:
                        print(f"\n\nCurrent epoch is: {int(i / batchsize)}\nThis {printevery} epochs took: {round(time.time() - start, 3)} seconds")
                        start = time.time()
                    else:
                        print(f"\n\nCurrent epoch is: {int(i / batchsize)}")
                        start = time.time()

        if storedata != None:
            return storedata
    def predwithout(self, inputs, outputs):
        av = [0 for i in range(len(outputs[0]))]
        outputlist = []
        for i in range(len(inputs)):
            chosenin = inputs[i]
            chosenout = outputs[i]
            for layer in self.layers:
                if layer.type == "fullcon":
                    chosenin = layer.forwardpass(chosenin)
                elif layer.type == "endlayer":
                    predout, cost = layer.out(chosenin, chosenout)
                    av = [cost[i] + av[i] for i in range(len(cost))]
                    print("Input was: " + str(inputs[i]) + ", target output was: " + str(outputs[i]) + ", predicted output was: " + str([float(s) for s in predout]))
                    outputlist.append([inputs[i], outputs[i], predout])
        print("Average cost was: " + str([float(i / len(inputs)) for i in av]))
        return outputlist
    def pred(self, inputs):
        outputlist = []
        for i in range(len(inputs)):
            chosenin = inputs[i]
            for layer in self.layers:
                if layer.type == "fullcon":
                    chosenin = layer.forwardpass(chosenin)
                elif layer.type == "endlayer":
                    predout = layer.pred(chosenin)
                    outputlist.append([inputs[i], predout])
        return outputlist
    def applywb(self, wb):
        curwb = 0
        for layer in self.layers:
            if layer.type == "fullcon":
                layer.loadwb(wb[curwb])
                curwb += 1
    def returnwb(self):
        wb = []
        for layer in self.layers:
            if layer.type == "fullcon":
                wb.append(layer.returnwb())
        return wb



def raiseinvalidlayer():
    raise RuntimeError("Layer is invalid")

def create(layers):
    return network([layer if any(layer.type == name for name in layertypes) else raiseinvalidlayer() for layer in layers])