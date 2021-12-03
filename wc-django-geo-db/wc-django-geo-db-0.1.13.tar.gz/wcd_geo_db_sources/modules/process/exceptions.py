class ProcessError(Exception):
    pass


class ProcessCantProceed(ProcessError):
    underlying_exception: Exception

    def __init__(self, *a, exception: Exception = None, **kw):
        self.underlying_exception = exception


class ProcessFinished(ProcessError):
    pass


class ProcessParallelExecution(ProcessError):
    pass


class ProcessNoStage(ProcessError):
    pass


class ProcessNoRunner(ProcessError):
    pass


class ProcessCantRerun(ProcessError):
    pass
