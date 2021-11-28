from copy import deepcopy

class SciPyFST:
    def __init__(self, states:list=[], initState=None, inAlphabet:list=[], outAlphabet:list=[], transitionFunction:list=[], outputFunction:list=[]):
        self.states = sorted(dict.fromkeys(states))#, key=str)
        """ states = [0,1,2] """

        self.initState = deepcopy(initState)
        """ initState = 0 """

        self.inAlphabet = sorted(dict.fromkeys(inAlphabet))#, key=str)
        """ inAlphabet = [0,1] """

        self.outAlphabet = sorted(dict.fromkeys(outAlphabet))#, key=str)
        """ outAlphabet = [0,1,2] """

        self.transitionFunction = deepcopy(transitionFunction)
        """ transitionFunction [ [State, inAlphabet, nextState], ...]\n
        transitionFunction = [ [0,0,1], [1,0,1], [1,1,2] ] """

        self.outputFunction = deepcopy(outputFunction)
        """
        outputFunction Moore [ [State, outAlphabet], ...]\n
        outputFunction = [ [0,0], [1,0], [2,2]]\n
        outputFunction Mealy [ [State, inAlphabet, outAlphabet], ...]\n
        outputFunction = [ [0,1,0], [1,1,0], [2,2,2]]
        """

        self.__type = self.__detTypeByOutputFunction()

        self.states = sorted(dict.fromkeys(self.states + self.__getStatesFromTransitionAndOutputFunction()))#, key=str)
        self.inAlphabet = sorted(dict.fromkeys(self.inAlphabet + self.__getInAlphabetFromTransitionAndOutputFunction()))#, key=str)
        self.outAlphabet = sorted(dict.fromkeys(self.outAlphabet + self.__getOutAlphabetFromTransitionAndOutputFunction()))#, key=str)

        self.trFuncDict = dict()
        for (curentState, inSignal, nextState) in self.transitionFunction:
            self.trFuncDict[curentState, inSignal] = nextState

        self.outFuncDict = dict()
        if self.isMoore():
            for (curentState, outSignal) in self.outputFunction:
                self.outFuncDict[curentState] = outSignal
        else:
            for (curentState, inSignal, outSignal) in self.outputFunction:
                self.outFuncDict[curentState, inSignal] = outSignal

        self.comboStateAndOutDict = dict()
        for (curentState, inSignal, nextState) in self.transitionFunction:
            if self.isMoore():
                self.comboStateAndOutDict[curentState, inSignal] = [nextState, self.outFuncDict.get(curentState)]
            else:
                self.comboStateAndOutDict[curentState, inSignal] = [nextState, self.outFuncDict.get((curentState, inSignal))]



    def __detTypeByOutputFunction(self):
        if self.outputFunction:
            if len(self.outputFunction[0]) == 2:
                return 'Moore'
            return 'Mealy'
        return None

    def __getStatesFromTransitionAndOutputFunction(self):
        toOut = []
        if self.initState is not None:
            toOut.append(self.initState)
        for (curentState, inSignal, nextState) in self.transitionFunction:
            if curentState is not None:
                toOut.append(curentState)
            if nextState is not None:
                toOut.append(nextState)
        if self.isMoore():
            for (curentState, outSignal) in self.outputFunction:
                if curentState is not None:
                    toOut.append(curentState)
        else:
            for (curentState, inSignal, outSignal) in self.outputFunction:
                if curentState is not None:
                    toOut.append(curentState)
        return sorted(dict.fromkeys(toOut))#, key=str)

    def __getInAlphabetFromTransitionAndOutputFunction(self):
        toOut = []
        for (curentState, inSignal, nextState) in self.transitionFunction:
            toOut.append(inSignal)
        if self.isMealy():
            for (curentState, inSignal, outSignal) in self.outputFunction:
                toOut.append(inSignal)
        return sorted(dict.fromkeys(toOut))#, key=str)

    def __getOutAlphabetFromTransitionAndOutputFunction(self):
        toOut = []
        if self.isMoore():
            for (curentState, outSignal) in self.outputFunction:
                if outSignal is not None:
                    toOut.append(outSignal)
        else:
            for (curentState, inSignal, outSignal) in self.outputFunction:
                if outSignal is not None:
                    toOut.append(outSignal)
        return sorted(dict.fromkeys(toOut))#, key=str)

    def isValid(self):
        """ Check TODO more checks needed """
        if self.initState not in self.states:
            return False
        # TODO more checks needed
        return True

    def getType(self):
        """
        Return FST type as string - "Moore" or "Mealy"
        """
        return self.__type

    def setType(self, typeString='Moore'):
        """
        Set FST type - "Moore" or "Mealy"
        """
        if typeString in ['Moore', 'Mealy']:
            if not self.outputFunction:
                self.__type = typeString
                return True
            dem = True
            for out in self.outputFunction:
                if (typeString == 'Moore' and len(out) != 2) or (typeString == 'Mealy' and len(out) != 3):
                    dem = False
                    break
            if dem:
                self.__type = typeString
                return True
        return False

    def deepcopy(self):
        fst = SciPyFST(self.states, self.initState, self.inAlphabet,\
            self.outAlphabet, self.transitionFunction, self.outputFunction)
        return fst

    def addState(self, state):
        if state not in self.states:
            self.states.append(state)
            self.states = sorted(dict.fromkeys(self.states))#, key=str)
        return True

    def addTransition(self, curentState, inSignal, nextState):
        self.addState(curentState)
        self.addState(nextState)
        if [curentState, inSignal, nextState] not in self.transitionFunction:
            self.transitionFunction.append([curentState, inSignal, nextState])
        self.trFuncDict[curentState, inSignal] = nextState
        return True

    def isMoore(self):
        """
        Return True if self.getType() == 'Moore' else False
        """
        return True if self.getType() == 'Moore' else False

    def isMealy(self):
        """
        Return True if self.getType() == 'Mealy' else False
        """
        return True if self.getType() == 'Mealy' else False

    def getNextState(self, curentState, inSignal, ifNotInDict=None):
        nextSate = self.trFuncDict.get((curentState, inSignal), ifNotInDict)
        if nextSate is None:
            return ifNotInDict
        return nextSate

    def getOutSignal(self, curentState, inSignal, ifNotInDict=None):
        if self.isMoore():
            outSignal = self.outFuncDict.get(curentState, ifNotInDict)
        else:
            outSignal = self.outFuncDict.get((curentState, inSignal), ifNotInDict)
        if outSignal is None:
            return ifNotInDict
        return outSignal

    def playFST(self, inSignals: list):
        outSignals = []
        curentState = self.initState
        outStates = []
        for inSignal in inSignals:
            outStates.append(curentState)
            outSignals.append(self.getOutSignal(curentState, inSignal, -1))
            curentState = self.getNextState(curentState, inSignal)#, curentState)
        if self.isMoore():
            outStates.append(curentState)
            outSignals.append(self.getOutSignal(curentState, inSignal, -1))

        return outSignals, outStates

    def playToWave(self, inSignals: list, hscale=1, useLogic=False):
        """
        { "signal": [
        { "name": "CLK",  "wave": "p......." },
        { "name": "CMD",  "wave": "x.3x=x4x=x=x=x=x", "data": ["RAS", "NOP"] },
        { "name": "STT",  "wave": "x.=x..=x........", "data": "ROW COL" }
        { "name": "OUT",  "wave": "z.......0.1010z.", "data": "ROW COL" }
        ]}
        """
        useLogicForStates = False
        curentState = self.initState
        waveCLK = "{ \"name\": \"CLK\",  \"wave\": \"P."
        waveRST = "{ \"name\": \"RST\",  \"wave\": \"10"
        waveCMD = "{ \"name\": \"CMD\",  \"wave\": \"zz"
        dataCMD = "\", \"data\": ["
        waveSTT = "{ \"name\": \"STT\",  \"wave\": \"x"
        dataSTT = "\", \"data\": ["
        waveOUT = "{ \"name\": \"OUT\",  \"wave\": \"x"
        dataOUT = "\", \"data\": ["
        prefixCMD = ""
        prefixSTT = ""
        prefixOUT = ""
        oldCMD = None
        oldSTT = None
        oldOUT = None
        # fix state after "reset"
        if self.isMealy():
            if useLogicForStates and useLogic and curentState in [0, 1]:
                waveSTT += str(curentState)
            else:
                waveSTT += "="
                dataSTT += "{prefix}\"{val}\"".format(prefix = prefixSTT, val = curentState)
                prefixSTT = ", "
            oldSTT = curentState
            waveOUT += "x"

        # play FST and draw Wave
        for inSignal in inSignals:
            waveCLK += "."
            waveRST += "."
            # Draw inSignal - CMD
            if oldCMD == inSignal:
                waveCMD += "."
            else:
                if useLogic and inSignal in [0, 1]:
                    waveCMD += str(inSignal)
                else:
                    waveCMD += "="
                    dataCMD += "{prefix}\"{val}\"".format(prefix = prefixCMD, val = str(inSignal))
                    prefixCMD = ", "
            # Draw States - STT
            if oldSTT == curentState:
                waveSTT += "."
            else:
                if useLogicForStates and useLogic and curentState in [0, 1]:
                    waveSTT += str(curentState)
                else:
                    waveSTT += "="
                    dataSTT += "{prefix}\"{val}\"".format(prefix = prefixSTT, val = str(curentState))
                    prefixSTT = ", "
            # Draw outSignal - OUT
            curentOUT = self.getOutSignal(curentState, inSignal, '...')
            if oldOUT == curentOUT:
                waveOUT += "."
            else:
                if useLogic and curentOUT in [0, 1]:
                    waveOUT += str(curentOUT)
                else:
                    waveOUT += "="
                    dataOUT += "{prefix}\"{val}\"".format(prefix = prefixOUT, val = str(curentOUT))
                    prefixOUT = ", "
            # keep old value
            oldCMD = inSignal
            oldSTT = curentState
            oldOUT = curentOUT
            curentState = self.getNextState(curentState, inSignal, curentState)
        waveCLK += "\" },"
        waveRST += "\" },"
        waveCMD += dataCMD + "],\"phase\":" + str(0.85 * hscale) + "},"
        waveSTT += dataSTT + "] },"
        waveOUT += dataOUT + "],\"phase\":" + ( str(-0.2 * hscale) if self.isMealy() else "0" ) + "}"
        wave = "{ \"signal\": [" + waveCLK + waveRST + waveCMD + waveSTT + waveOUT + "],\"config\":{\"hscale\":" + str(hscale) + "}}"
        return wave

    def toDot(self):
        """
        !!! DRAFT !!!
        Output example:\n
        digraph fst {\n
            rankdir=LR;\n
            node [shape = point ]; none\n
            node [shape = doublecircle]; 0; # initState\n
            none -> 0;\n
            node [shape = circle]; 0 1; # states\n
            node [style=filled, fillcolor=red];\n
            0 -> 1 [ label = 2 ]; # State -> nextState [ label = "inAlphabet" ]\n
            0 -> 0 [ label = 1 ];\n
            1 -> 0 [ label = 0 ];\n
            1 -> 2 [ label = 0 ];\n
            2 -> 1 [ label = 2 ];\n
            2 -> 2 [ label = 0 ];
        }
        """

        ifNotInDict = '-'
        outString = "digraph fst {\n\trankdir=LR;\n\tnode [shape=point]; start;\n\tnode [shape=circle];"
        if self.isMoore():
            outString += " \"{initState}\" [label=\"{initState}/{outSignal}\"];".format(
                initState = str(self.initState), outSignal = self.getOutSignal(self.initState, None, ifNotInDict))
        else:
            outString += " \"{initState}\" [label=\"{initState}\"];".format(initState = str(self.initState))
        outString += "\n\tstart -> \"{initState}\" [label=start];\n\tnode [shape=circle];".format(initState = str(self.initState))
        for state in self.states:
            if state != self.initState:
                if self.isMoore():
                    outString += "\n\t\"{state}\" [label=\"{state}/{outSignal}\"];".format(
                        state = state, outSignal = self.getOutSignal(state, None, ifNotInDict))
                else:
                    outString += "\n\t\"{state}\" [label=\"{state}\"];".format(state = state)
        outString += "\n\tnode [style=filled, fillcolor=hotpink];"
        for (state, inSignal, nextState) in self.transitionFunction:
            if nextState is None:
                nextState = ifNotInDict
            if self.isMoore():
                outString += "\n\t\"{state}\" -> \"{nextState}\" [label={inSignal}];".format(
                    state = str(state), nextState = str(nextState), inSignal = str(inSignal))
            else:
                outString += "\n\t\"{state}\" -> \"{nextState}\" [label=\"{inSignal}/{outSignal}\"];".format(
                    state = str(state), nextState = str(nextState), inSignal = str(inSignal),
                    outSignal = self.getOutSignal(state, inSignal, ifNotInDict))
        outString += "\n}"
        return outString

    def toMdTable(self):
        """
        !!! DRAFT !!!
        Output example:\n
        | Input \\ State | q0  | q1  | q2  | q3  |
        |:--------------:|:---:|:---:|:---:|:---:|
        |       0        | ... | ... | ... | q0  |
        |       1        | ... | q2  | ... | ... |
        |       2        | ... | ... | ... | ... |
        """

        outString = "| Input \\ State |"
        if self.isMoore():
            for state in self.states:
                outString += " {state}/{outSignal} |".format(state = state, outSignal = self.getOutSignal(state, None, "-"))
        else:
            for state in self.states:
                outString += " {state} |".format(state = state)
        outString += "\n|:---:|"
        for state in self.states:
            outString += ":---:|"
        outString += "\n"
        for inSignal in self.inAlphabet:
            outString += "| {inSignal} |".format(inSignal = inSignal)
            for curentState in self.states:
                tempVal = self.getNextState(curentState, inSignal)
                if tempVal is not None:
                    if self.isMoore():
                        outString += " {nextState} |".format(nextState = tempVal)
                    else:
                        outString += " {nextState}/{outSignal} |".format(nextState = tempVal, outSignal = self.getOutSignal(curentState, inSignal, "-"))
                else:
                    if self.isMoore():
                        outString += " - |"
                    else:
                        outString += " -/{outSignal} |".format(nextState = tempVal, outSignal = self.getOutSignal(curentState, inSignal, "-"))
            outString += "\n"
        return outString

    def asMoore(self):
        if self.isMoore():
            return self.deepcopy()

        initStateMoore = 0
        #initStateSignalMoore = -1
        newMooreState_qi = initStateMoore # q0 without q
        markedTranOut = dict() # key - [topHeaderState_Si, leftHeaderSignal_Xj], val - existMooreState_qi. See point (1)
        dictForSearchNewState = dict() # key - [tableState_Sm, tableSignal_Yn] from table, val - existMooreState_qi. See point (1)
        eqStatesFor_Si = dict() # key - tableState_Sm, val - list of existMooreState_qi [0, 2, ...]. See point (2)

        outputFunctionMoore = [] # list [[state, outSignal], [...] ... ]. See point (3)

        # add q0 state to S0
        #mapForSearchNewState[self.initState, None] = newMooreState_qi
        eqStatesFor_Si[self.initState] = [newMooreState_qi]
        #outputFunctionMoore.append([newMooreState_qi, initStateSignalMoore])

        # mark all equivalent transition-output pair as new Moore states. See point (1) & (2)
        for topHeaderState_Si in self.states:
            for leftHeaderSignal_Xj in self.inAlphabet:
                tableState_Sm = self.getNextState(topHeaderState_Si, leftHeaderSignal_Xj)
                tableSignal_Yn = self.getOutSignal(topHeaderState_Si, leftHeaderSignal_Xj)
                existMooreState_qi = dictForSearchNewState.get((tableState_Sm, tableSignal_Yn)) # (1)
                if existMooreState_qi is None:
                    newMooreState_qi += 1
                    existMooreState_qi = newMooreState_qi
                    dictForSearchNewState[(tableState_Sm, tableSignal_Yn)] = existMooreState_qi # (1) add new state
                    outputFunctionMoore.append([existMooreState_qi, tableSignal_Yn])
                    tempList = eqStatesFor_Si.get(tableState_Sm, []) # (2)
                    tempList.append(newMooreState_qi)
                    eqStatesFor_Si[tableState_Sm] = tempList
                markedTranOut[topHeaderState_Si, leftHeaderSignal_Xj] = existMooreState_qi

        # create transition table (4)
        transitionFunctionMoore = []
        for key_Si, list_qj in eqStatesFor_Si.items():
            for qj in list_qj:
                for signal in self.inAlphabet:
                    transitionFunctionMoore.append([qj, signal, markedTranOut.get((key_Si, signal))])

        return SciPyFST([], initStateMoore, [], [], transitionFunctionMoore, outputFunctionMoore)

    def getTestSignal(self):
        listOfInSignalsList = []
        def recGetNext(curentState, visitedStates:dict, inSignals:list):
            if visitedStates.get(curentState) is None:
                visitedStates[curentState] = 1
                for inSignal in self.inAlphabet:
                    copyOfInSignals = deepcopy(inSignals)
                    copyOfInSignals.append(inSignal)
                    nextCurentState = self.getNextState(curentState, inSignal)
                    if nextCurentState is None:
                        listOfInSignalsList.append(copyOfInSignals)
                        return
                    else:
                        recGetNext(nextCurentState, deepcopy(visitedStates), copyOfInSignals)
            else:
                listOfInSignalsList.append(inSignals)
                return
        recGetNext(self.initState, dict(), [])
        return listOfInSignalsList

    def isContains(self, fst):
        listOfInSignalsList = fst.getTestSignal()
        selfType = 1 if self.isMoore() else 0
        fstType = 1 if fst.isMoore() else 0
        for inSignalList in listOfInSignalsList:
            if self.playFST(inSignalList)[0][selfType:] != fst.playFST(inSignalList)[0][fstType:]:
                return False
        return True

    def isSimilar(self, fst):
        return self.isContains(fst) and fst.isContains(self)
