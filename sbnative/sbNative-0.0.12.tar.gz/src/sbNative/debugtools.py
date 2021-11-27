import inspect
import os
import sys
import time
import atexit
import typing
import itertools
from enum import Enum
from runtimetools import getPath
import webbrowser


global terminalStacking
terminalStacking = False

global prevLogInfo
global prevLog
global lineSplitSign

lineSplitSign = "\uF8FF"

prevLogInfo = {
    "infoName": None,
    "tracebackDepth": None,
    "separator": None,
    "end": None,
    "args": [],
    "kwargs": {},
    "fileName": None,
    "lineNumber": None
}

prevLog = ["", 1]


def switchTerminalStacking() -> bool:
    '''
    Terminalstacking is a feature that prevents the logging function from spamming the terminal with useless information.
    If the same things are logged in the same line, file, back to back and this feature is enabled, the information will not be printed again,
    it will rather "edit" the existing line and add `[2x]` `[3x]` `[4x]` ... `[nx]` after the location of the log.
    '''
    global terminalStacking
    terminalStacking = not terminalStacking
    if not terminalStacking:
        print(f"{prevLog[0]} [{prevLog[1]}x]")

    def printNewlineOnTerminalStack():
        global terminalStacking
        if terminalStacking:
            print()

    atexit.register(printNewlineOnTerminalStack)
    return terminalStacking


def computeLinebreakIndents(args: object, kwargs: dict, indentStartEnd: typing.Union[str, typing.Sequence[typing.Tuple[str, str]]] = None) -> list:
    '''
    Used for clean representation of e.g. Lists (indentStartEnd = "[]") if multiple lines are necessary.
    If `indentStartEnd` is `None` all the arguments will be combined to a list of newlines.
    IndentStartEnd must be a 2 item sequence of single characters. Multi Character support might be supported in the future.
    '''
    args = tuple(args) + tuple([f"{k} = {v}" for k,v in kwargs.items()])
    ret = []

    currIndentLvl = 0

    if indentStartEnd:
        srt, end = indentStartEnd
        for a in args:
            lnsUnsplitted = str(a).replace(
                srt, srt + lineSplitSign).replace(end, lineSplitSign + end).replace(end + ", ", end + f",{lineSplitSign}")
            lines = lnsUnsplitted.split(lineSplitSign)
            for l in lines:
                currIndentLvl -= l.count(end) * 4
                ret.append(" " * currIndentLvl + l)
                currIndentLvl += l.count(srt) * 4

    else:
        for a in args:
            ret += [str(a)]
    return ret


def __baseLoggingFunc(
        infoName: typing.Union[str, None],
        tracebackDepth: int,
        separator: str,
        maxOccupyableWidthPortion: float,
        end: str,
        *args: object,
        **kwargs) -> None:
    '''
    This is the base of the logging function,
    like `log` and `ilog` (infolog). It is almost redundant to use this,
    because the `log` and `ilog` functions will likely satisfy your needs.
    '''
    global terminalStacking

    call = inspect.getframeinfo(inspect.stack()[tracebackDepth][0])
    fileName, lineNumber = call.filename, call.lineno

    if terminalStacking:
        global prevLogInfo
        global prevLog

        currLogInfo = {
            "infoName": infoName,
            "tracebackDepth": tracebackDepth,
            "separator": separator,
            "end": end,
            "args": args,
            "kwargs": kwargs,
            "fileName": fileName,
            "lineNumber": lineNumber
        }

        if currLogInfo == prevLogInfo:
            prevLog[1] += 1
            print(f"{prevLog[0]} [{prevLog[1]}x]", end="\r")
            return

        if len(prevLog[0]):
            print(f"{prevLog[0]}")

        prevLogInfo = currLogInfo

    path = fileName.replace("\\", "/") + ":" + str(lineNumber)
    arrow = " --> "

    if infoName:
        logString = f"LOG ({repr(infoName)}): "
    else:
        logString = f"LOG: "

    argStrings = computeLinebreakIndents(args, kwargs)
    consoleWidth = os.get_terminal_size()[0]
    occupiedLogLength = sum([len(s)+len(separator)
                            for s in argStrings])-len(separator)

    if occupiedLogLength+len(path)+len(arrow)+len(logString)+len(end) > consoleWidth*maxOccupyableWidthPortion:
        separator = "\n"
        logString += "\n"
        arrow = "\n" + arrow[1:]
        argStrings = computeLinebreakIndents(args, kwargs, indentStartEnd="()")
        argStrings = computeLinebreakIndents(argStrings, kwargs, indentStartEnd="[]")
        argStrings = computeLinebreakIndents(argStrings, kwargs, indentStartEnd="{}")

    argStr = separator.join(argStrings).replace(lineSplitSign, "")

    logString += f"{argStr}{end}{arrow}{path}"

    if terminalStacking:
        print(logString.split("\n")[-1], end="\r")
        prevLog = [logString, 1]
    else:
        print(logString)


def log(*args: object, depth: int = 2, **kwargs) -> None:
    '''
    Prints all the arguments given to the console and the file + line of the call.
    Supports more advanced logging when paired with the `cleanRepr` class decorator.
    '''
    __baseLoggingFunc(None, depth, " | ", .9, "", *args, **kwargs)


def ilog(info: object, *args: object, depth: int = 2, end: str = "", **kwargs) -> None:
    '''
    Prints all the arguments given to the console and the file + line of the call.
    First argument will be used to represent what is logged. Supports more advanced logging when paired with the `cleanRepr` class decorator.
    '''
    __baseLoggingFunc(info, depth, " | ", .9, end, *args, **kwargs)


def __clsRepr(cls: type) -> type:
    '''
    This is what the `__repr__` method of the class decorated with `cleanRepr` decorator is replaced with.
    Supports newlines with the logging functions.
    '''
    isLogCall = isFromCall("log")
    ret = f"{type(cls).__name__}("

    subObjects = {**cls.__dict__, **{name: classAttr for name, classAttr in type(
        cls).__dict__.items() if not callable(classAttr) and not name.startswith("__")}}

    for k, v in subObjects.items():
        if k in cls.__excludeReprVarNames__:
            continue

        ret += f"{repr(k)} = {repr(v)}, "
        if isLogCall:
            ret += lineSplitSign

    if len(subObjects) == 0:
        return ret + ")"

    ret = ret.strip(lineSplitSign)

    remvLastChars = -1

    if len(subObjects) > 1:
        remvLastChars -= 1

    if remvLastChars == 0:
        return ret + ")"
    return ret[:remvLastChars] + ")"


def __clsLog(self, *args) -> object:
    if len(args) == 0:
        return log(self, depth=3)
    return ilog(self, *args, depth=3)


def isFromCall(funcName: str) -> bool:
    '''
    Gets if a function with the name `funcName` is in the callstack.
    Used by `__clsRepr` to determine if it should add markers in the form of `lignSplitSign` where newlines can be added if the logging string is too long.
    '''
    funcs = [c.function for c in inspect.stack()]
    return funcName in funcs


def cleanRepr(*exclude: typing.Iterable[str]) -> type:
    '''
    A decorator which makes the representation of your class as clean as possible.
    If you don't want specific class or instance variables to be included, you may specify them as arguments for this function.
    '''
    def decorator(cls):
        cls.__excludeReprVarNames__ = exclude
        cls.__repr__ = __clsRepr
        cls.log = __clsLog
        return cls

    return decorator


def getTerminalOutputs(func: typing.Callable, *args, **kwargs) -> typing.Tuple[str, object]:
    '''Returns the terminal output content recorded while the function was running, and the result from the function in a tuple.
    (TerminalOutput,FunctionResult)'''
    originalStdout = sys.stdout

    with open('terminalOutputTest.temp', 'w') as f:
        sys.stdout = f
        funcResult = func(*args, **kwargs)
        sys.stdout = originalStdout

    with open('terminalOutputTest.temp', 'r') as f:
        ret = f.read()

    os.remove('terminalOutputTest.temp')
    return ret, funcResult


def plotTuples(plt, tups, title="", xaxisName="", yaxisName="") -> None:
    valsOld = list(zip(*tups))

    vals = [tuple([str(i) if type(i) not in [str, int, float]
                  else i for i in row]) for row in valsOld]

    if vals != valsOld:
        print("WARNING: CASTED ITEMS IN THE TUPLE TO BE COMPREHENSABLE TO MATPLOTLIB")
        print(valsOld)
        print("-->")
        print(vals)

    if any(type(v) not in [str, int, float] for v in itertools.chain(*vals)):
        raise TypeError(
            "Attributes in x or y which are not strings, integers or floats!")

    plt.plot(*vals)
    plt.title(title)
    plt.xlabel(xaxisName)
    plt.ylabel(yaxisName)


def timer(func: callable) -> typing.Callable:
    '''
    A simple decorator for timing the execution time of a function or method. Flexes the `ilog` function.
    '''
    def wrapper(*args, **kwargs):
        begin = time.time()
        ret = func(*args, **kwargs)
        ilog(f"Executing `{func.__name__}` took",
             time.time() - begin, depth=3, end=" seconds")
        return ret

    return wrapper


class tPlotArgs(Enum):
    TIME = 1
    ARGS = 2


class timePlotter:
    def __init__(self, sortAfter: typing.Union[tPlotArgs, tPlotArgs], trackArgs: typing.Sequence[int] = [], trackKwargs: typing.Sequence[str] = [], reverse=False):
        self.callArgsAndTimes = []
        self.sortAfter = sortAfter
        self.reverse = reverse
        self.func = None
        self.trackArgs = trackArgs
        self.trackKwargs = trackKwargs


    def timer(self, func: callable):
        '''
        A simple decorator for timing the execution time of a function or method. Uses matplotlib to show the time with arguments for the called function.
        '''
        if self.func is None:
            self.func = func
        
        else:
            raise RuntimeError("You may not decorate multiple functions with the same timing instance.")        

        def wrapper(*args, **kwargs):
            begin = time.time()
            ret = func(*args, **kwargs)

            self.callArgsAndTimes.append(
                    {"deltaT": 1000 * (time.time() - begin), "args": args, "kwargs": kwargs}
                )
            return ret

        return wrapper


    def show(self):
        if self.func is None:
            raise RuntimeError(f"A function was never called with this timePlotting instance.")

        tuples = []
        
        for i in self.callArgsAndTimes:
            argsAndKwargs = ""

            argsToPlot = tuple(a for idx,a in enumerate(i['args']) if idx in self.trackArgs)
            if str(argsToPlot) != "()":
                argsAndKwargs += str(argsToPlot)
                
            kwargsToPlot = {name:kwa for name,kwa in i['kwargs'].items() if name in self.trackKwargs}
            if str(kwargsToPlot) != "{}":
                argsAndKwargs += str(kwargsToPlot)

            if self.sortAfter is tPlotArgs.ARGS:
                tuples.append((argsAndKwargs, i["deltaT"]))

            elif self.sortAfter is tPlotArgs.TIME:
                tuples.append((i["deltaT"], argsAndKwargs))

            else:
                raise TypeError(f"{self.sortAfter} is not an attribute of the debugtools.tPlotArgs class!")
        

        with open(getPath().joinpath("templates").joinpath("graphTemplate.html"), "r") as rf:
            htmlTemplate = rf.read()
            htmlTemplate = self.inject(htmlTemplate, tuples)
        self.displayGraph(htmlTemplate)


    def inject(self, htmlTemplate, values):
        beginIdx = htmlTemplate.find("{BEGIN-TBL-ELM}")
        tblElm = htmlTemplate[beginIdx + len("{BEGIN-TBL-ELM}"):htmlTemplate.find("{END-TBL-ELM}")]

        elements = []
        for x,y in values:
            elements.append(
                    tblElm.replace("{XVALUE}", str(x)).replace("{YVALUE}",str(y))
                )

        
        htmlTemplate = htmlTemplate.replace(tblElm, "\n".join(elements))
        
        return htmlTemplate.replace("{BEGIN-TBL-ELM}","").replace("{END-TBL-ELM}","")

    def displayGraph(self, htmlContent):
        with open(f"{str(getPath())}/temp/graphdisplay.html",'w') as f:
            f.write(htmlContent)
            
            filename = f"file:///{str(getPath())}/temp/graphdisplay.html"
            webbrowser.get().open(filename)