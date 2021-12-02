"""A Python implementation of the EMuLSion framework.
(Epidemiologic MUlti-Level SImulatiONs).

Tools for providing a generic command line parser with useful options.

"""

import sys

from   pathlib               import Path
from   argparse              import ArgumentParser

import numpy                 as     np

from   emulsion.model        import EmulsionModel
from   emulsion.tools.state  import StateVarDict

class EmulsionParser(ArgumentParser):
    """A class for parsing command-line arguments in executable
    classes.

    WARNING: in Emulsion, this class should be considered
    deprecated. Use instead the emulsion.__main__ method based on
    `docopt`.

    """
    def __init__(self, parameters, version='', **kwargs):
        super().__init__(**kwargs)
        self.args = None
        self.model = None
        # define default values
        self.parameters = StateVarDict(parameters)
            # define line command arguments
        self.add_argument('-v', '--version',
                          action='version',
                          version='%(prog)s {}'.format(version),
                          help='Print the version of the program and exit.')
        self.add_argument('--show-params',
                          action='store_true',
                          dest='show_params',
                          help='Show the name of available parameters and'
                          ' exit.')
        self.add_argument('--model',
                          dest='model',
                          help='Location of the YAML file containing'
                          ' the model to run')
        self.add_argument('-p', '--param',
                          action='append',
                          dest='param',
                          help='Specify a value for a parameter, instead of'
                          ' the default value.')
        # self.add_argument('--id',
        #                   dest='id',
        #                   help='Specify the ID of the simulation')
        self.add_argument('--seed',
                          dest='seed',
                          type=int,
                          help='Set the seed for random numbers')
        self.add_argument('--output-dir',
                          dest='output_dir',
                          default='outputs',
                          help='Specify the directory for simulation outputs')
        self.add_argument('--test',
                          action='store_true',
                          dest='test',
                          help='Run the simulation in test mode')

    def do_parsing(self):
        """Execute the parsing step.

        """
        self.args = self.parse_args()
        if self.args.model:
            self.model = EmulsionModel(filename=self.args.model)
        else:
            self.model = EmulsionModel(filename=self.parameters.model_path)

        # if self.args.years:
        #     self.parameters.duration = int(self.args.years)

        # Define path for output
        self.parameters.output_dir = Path(self.args.output_dir)

        self.parameters.test = self.args.test

        if self.args.param:
            model_changes = {}
            modifiable = self.model.get_modifiable_parameters()
            for key, val in [p.split('=') for p in self.args.param]:
                if key in self.parameters:
                    self.parameters[key] = type(self.parameters[key])(val)
                elif key in modifiable:
                    model_changes[key] = val
                else:
                    print('Unknown parameter', key)
                    sys.exit(-1)
            if model_changes:
                self.model.change_parameter_values(model_changes)

        if self.args.seed:
            self.parameters.seed = self.args.seed
            np.random.seed(self.args.seed)

        if self.args.show_params:
            modifiable = self.model.get_modifiable_parameters()
            print('\n{: ^72}'.format('AVAILABLE PARAMETERS (with their current value)'))
            print('-'*72)
            print('PROGRAM PARAMETERS')
            print('-'*72)
            for key, val in self.parameters.items():
                print('  {:.<34}{!s:.>34}'.format(key, val))
            print('-'*72)
            print('MODEL PARAMETERS')
            print('-'*72)
            for key, val in modifiable.items():
                print('  {:.<34}{!s:.>34}'.format(key, val))
            sys.exit()
