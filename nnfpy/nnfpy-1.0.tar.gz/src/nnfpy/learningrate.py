class linearloss:
    def __init__(self, lossrate):
        self.lossrate = lossrate
        self.type = "loss"
    def newrate(self, learningrate):
        return learningrate - self.lossrate if learningrate - self.lossrate > 0 else learningrate

class timesloss:
    def __init__(self, lossrate):
        self.lossrate = lossrate
        self.type = "loss"
    def newrate(self, learningrate):
        return learningrate - learningrate * self.lossrate

class learnboost:
    def __init__(self, epochnum, boost):
        self.epochnum = epochnum
        self.boostam = boost
        self.type = "boost"
    def boost(self, epochs, learning):
        try:
            if epochs % self.epochnum == 0 and epochs != 0:
                return learning + self.boostam
            else:
                return learning
        except:
            return learning

class smartboost:
    def __init__(self, epochnum, boost, boostloss=1):
        self.epochnum = epochnum
        self.boostam = boost
        self.type = "smartboost"
        self.boostloss = boostloss
    def boost(self, epochs, learning, totalepochs):
        try:
            if epochs % self.epochnum == 0 and epochs != 0:
                return learning + self.boostam * (1 - epochs / totalepochs / self.boostloss)
            else:
                return learning
        except:
            return learning