from enum import Enum, auto


class RecoverFuncId(Enum):
    FIND_ELEMENT = auto()
    FIND_ELEMENTS = auto()
    ELEMENT_FIND_ELEMENT = auto()
    ELEMENT_FIND_ELEMENTS = auto()
    ELEMENT_CLICK = auto()


class RecoverData:
    def __init__(
        self,
        webdriver,
        func_id,
        function,
        args,
        kwargs,
        element=None,
        elements=None,
        exception=None,
        attempts=1,
        elapsed=0,
    ):
        self.webdriver = webdriver
        self.func_id = func_id
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.element = element
        self.elements = elements
        self.exception = exception
        self.attempts = attempts
        self.elapsed = elapsed
