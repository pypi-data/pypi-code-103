import sys


class Outfile:
    '''
    Redirect stdout to a file inside statements like:
    with Outfile(...):
        print(...)
    '''

    def __init__(self, outfile=None):
        self.outfile = outfile

    def __enter__(self):
        if self.outfile is not None:
            self.initial_stdout = sys.stdout
            sys.stdout = open(self.outfile, 'a')

    def __exit__(self, *args):
        if self.outfile is not None:
            sys.stdout.close()
            sys.stdout = self.initial_stdout
