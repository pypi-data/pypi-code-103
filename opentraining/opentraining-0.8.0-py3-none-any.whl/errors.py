class OpenTrainingError(Exception):
    '''Base class for all OpenTraining errors'''
    def __init__(self, msg, userdata):
        super().__init__(msg)
        self.userdata = userdata

class BadPath(OpenTrainingError):
    pass

class DependencyError(OpenTrainingError):
    pass

class PathNotFound(OpenTrainingError):
    pass

class NotCommitted(OpenTrainingError):
    pass

class AlreadyCommitted(OpenTrainingError):
    pass

class CompoundError(OpenTrainingError):
    '''An error that *contains* multiple errors. Used in situations where
    we do not bail out early, but rather continue, and represent the
    user with a list of collected error messages.  '''

    def __init__(self, msg, errors, userdata):
        super().__init__(msg, userdata=userdata)
        self.msg = msg
        self.errors = errors

    def __str__(self):
        msgs = [self.msg]
        for e in self.errors:
            msgs.append(' '*4 + str(e))
        return '\n'.join(msgs)

    def __iter__(self):
        yield CompoundError(self.msg, errors=[], userdata=self.userdata)
        for e in self.errors:
            if isinstance(e, CompoundError):
                yield from e
            else:
                yield e
