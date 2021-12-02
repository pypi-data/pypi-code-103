"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions for abstract agent management.

Exceptions

"""

#  ______                    _   _
# |  ____|                  | | (_)
# | |__  __  _____ ___ _ __ | |_ _  ___  _ __  ___
# |  __| \ \/ / __/ _ \ '_ \| __| |/ _ \| '_ \/ __|
# | |____ >  < (_|  __/ |_) | |_| | (_) | | | \__ \
# |______/_/\_\___\___| .__/ \__|_|\___/|_| |_|___/
#                     | |
#                     |_|

class StateVarNotFoundException(Exception):
    """Exception raised when a semantic error occurs during model parsing.

    """
    def __init__(self, statevar, source):
        super().__init__()
        self.statevar = statevar
        self.source = source

    def __str__(self):
        return 'Statevar %s not found in object %s' % (self.statevar,
                                                       self.source)

class LevelException(Exception):
    """Exception raised when a semantic error occurs during model parsing.

    """
    def __init__(self, cause, level):
        super().__init__()
        self.level = level
        self.cause = cause

    def __str__(self):
        return 'Level %s %s' % (self.level, self.cause)


class InvalidCompartmentOperation(Exception):
    """Exception raised when a compartiment is asked for impossible
    operations, such as adding numbers to a list of units.

    """
    def __init__(self, source, operation, params):
        super().__init__(self)
        self.source = source
        self.operation = operation
        self.params = params

    def __str__(self):
        return "%s cannot execute '%s' with params: '%s'" %\
            (self.source, self.operation, self.params)
