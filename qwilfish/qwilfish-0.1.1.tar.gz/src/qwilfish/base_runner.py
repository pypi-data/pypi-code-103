class BaseRunner:
    '''Base class for creating test cases from the fuzzed input'''

    RET_PASS = "PASS"
    RET_FAIL = "FAIL"
    RET_URES = "UNRESOLVED"

    def __init__(self):
        '''Initialize'''
        pass

    def run(self, input):
        '''Deliver the input to the SUT and return result and whatever
        quantities are being monitored'''
        print(input)
        return (input, BaseRunner.RET_URES)
