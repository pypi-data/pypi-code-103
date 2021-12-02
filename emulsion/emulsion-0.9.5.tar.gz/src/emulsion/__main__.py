"""Usage:
    emulsion check MODEL [options]
    emulsion generate MODEL
    emulsion run [--plot] MODEL [options] [(-p KEY=VALUE)...]
    emulsion show MODEL [options] [(-p KEY=VALUE)...]
    emulsion plot MODEL [options]
    emulsion sensitivity MODEL DESIGN [options]
    emulsion change MODEL NEW_MODEL (-p KEY=VALUE)...
    emulsion (-h | --help | -V | --version)

Commands:
  check MODEL                 Check the syntactic correctness of the given MODEL
                              (path to YAML file of the model to run), according
                              to the META-model expressed as a textX grammar
                              file (specified by option '--metamodel'). Option
                              '--view-meta' generates a figure representing
                              Emulsion META-model. If the model is correct,
                              option '--view-model' also generates a figure for
                              the MODEL structure.
  generate MODEL              Generate a skeleton to help writing specific
                              pieces of code before the MODEL can be run, and
                              exit.
  run MODEL                   Run simulations based on the specified MODEL (path
                              to YAML file of the model to run).
  show MODEL                  Print all MODEL parameters and exit.
  plot MODEL                  Plot outputs for specified MODEL (based on
                              previous runs), save figures and exit.
  sensitivity MODEL DESIGN    Run a sensitivity analysis for the specified MODEL
                              using the provided experimental DESIGN.
                              NOT IMPLEMENTED YET.
  change MODEL NEW_MODEL      Modify the initial MODEL into a NEW_MODEL using
                              appropriate options, and exit. NOT IMPLEMENTED YET

Options:
  -h --help                   Display this page and exit.
  -V --version                Display version number and exit.
  -r RUNS --runs RUNS         Specify the number of repetitions of the same
                              model [default: 10].
  -t STEPS --time STEPS       Specify the number of steps to run in each
                              repetition. If the model defines a total_duration,
                              it is used as time limit, unless the '-t' option
                              is explicitly specified. Otherwise, the default
                              value is 100 steps.
  --level LEVEL               Specify the LEVEL (scale) for running the model.
                              Valid values are those defined in the 'level'
                              section of the MODEL. The corresponding agent
                              class will be used to manage the simulation of
                              lower-level entities. [default: herd].
  --plot                      Plot outputs just after running the model.
  --metamodel META            Specify a metamodel for syntax checking
                              [default: scripts/emulsion.tx]
  --view-model                Output a figure for the model if it complies to
                              EMuLSion DSL syntax (requires Graphviz).
  --view-meta                 Output a figure for the meta-model (requires
                              Graphviz).
  --seed SEED                 Set a seed value for random numbers. When not
                              specified, the seed is set according to system
                              time and the process id.
  --show-seed                 Print the seed used for random numbers.
  -p KEY=VAL --param KEY=VAL  Change parameter named KEY to the specified VALue.
  --view-machines             Draw diagrams to represent the state machines of
                              the model (requires Graphviz).
  --output-dir OUTPUT         Specify a directory for simulation outputs
                              [default: outputs].
  --input-dir INPUT           Specify a directory for simulation inputs
                              [default: data].
  --figure-dir FIG            Specify a directory for graphic outputs (figures)
                              [default: img].
  --format FORMAT             Specify an image format for diagram outputs
                              [default: png].
  --echo                      Just print command-line arguments parsed by Python
                              docopt module and exit.
  --deterministic             Run the simulation in deterministic mode if
                              available.
  --test                      Run the simulation in test mode. NOT USED YET.
  --init INIT_FILE            Speficy a file for initial conditions.
                              NOT USED YET.
"""

import sys
import os
import time
import subprocess
import datetime                     as dt

from   pathlib                      import Path

import yaml
import numpy                        as np

from   docopt                       import docopt
from   textx                        import metamodel_from_file
from   textx.export                 import metamodel_export, model_export

from   emulsion.model               import EmulsionModel
from   emulsion.tools.state         import StateVarDict
from   emulsion.tools.misc          import load_class
from   emulsion.tools.plot          import plot_outputs
from   emulsion.tools.simulation    import MultiSimulation

DEFAULT_VERSION = "0.9.5"

def get_version():
    """Retrieve the GIT version number of current program.

    """
    if not os.path.isdir(".git"):
        # print("This does not appear to be a Git repository."
        #       "\nLast known version number is:")
        return DEFAULT_VERSION
    try:
        proc = subprocess.Popen(["git", "describe",
                                 "--tags", "--dirty", "--always"],
                                stdout=subprocess.PIPE)
    except EnvironmentError:
        print("unable to run git")
        return 'Unknown'
    stdout = proc.communicate()[0].strip().decode('utf-8')
    if proc.returncode != 0:
        print("unable to run git")
        return 'Unknown'
    return stdout


def change_parameters(params, change_list):
    """Change either the model or local parameters according to the list
    of new values.

    """
    model_changes = {}
    modifiable = params.model.get_modifiable_parameters()
    for key, val in [p.split('=') for p in change_list]:
        if key in params:
            params[key] = type(params[key])(val)
        elif key in modifiable:
            model_changes[key] = val
        else:
            print('Unknown parameter:', key)
            sys.exit(-1)
    if model_changes:
        params.model.change_parameter_values(model_changes)

def show_parameters(params):
    """Display all parameters involved in the current program and model
    and exit.

    """
    modifiable = params.model.get_modifiable_parameters()
    print('\n{: ^72}'.format('AVAILABLE PARAMETERS (with their current value)'))
    print('-'*72)
    print('PROGRAM PARAMETERS')
    print('-'*72)
    for key, val in params.items():
        print('  {:.<34}{!s:.>34}'.format(key, val))
    print('-'*72)
    print('MODEL PARAMETERS')
    print('-'*72)
    for key, val in modifiable.items():
        print('  {:.<34}{!s:.>34}'.format(key, val))
    sys.exit()


def generate_model(params):
    """Generate a skeleton for the pieces of specific code to write.

    """
    model = params.model
    src_path = Path(__file__).parent.parent
    modules = sorted(set([level_desc['module']
                          for level_desc in model.levels.values()
                          if not level_desc['module'].startswith('emulsion.agent')
    ]))
    for module in modules:
        mod_path = Path(src_path, *module.split('.')).with_suffix('.py')
        if mod_path.exists():
            print('WARNING, file %s already exists, ' % (mod_path,), end='')
            mod_path = mod_path.with_suffix('.py.%s' %
                                            (dt.datetime.now().timestamp()))
            print('writing in %s instead' % (mod_path,))
        print('GENERATING CODE SKELETON %s\nFOR MODULE %s' %
              (mod_path, module,))
        with open(mod_path, 'w') as f:
            print(model.generate_skeleton(module), file=f)


def run_model(params):
    """Run the model with the specified local parameters.

    """
    count_path = Path(params.output_dir, 'counts.csv')
    if count_path.exists():
        count_path.unlink()
    multi_simu = MultiSimulation(**params)
    # multi_simu.write_dot()
    start = time.perf_counter()
    multi_simu.run()
    end = time.perf_counter()
    print('Simulation finished in {:.2f} s'.format(end-start))
    print('Outputs stored in %s' % (count_path,))


def view_machines(params):
    """Use Graphviz to render state machines of the model.

    """
    model = params.model
    model.write_dot(params.output_dir)
    prefix = model.model_name
    for name, _ in model.state_machines.items():
        inpath = Path(params.output_dir, prefix + '_' + name + '.dot')
        outpath = Path(params.figure_dir,
                       prefix + '_' + name + '_machine.' + params.img_format)
        os.system("dot -T%s %s > %s" % (params.img_format, inpath, outpath))
        print('Generated state machine diagram %s' % (outpath,))

def check_model(params, filemodel, metamodel,
                view_meta=False, view_model=False):
    """Check the syntax of the model according to the grammar specified in
    the metamodel. If `show_meta` is True, produce a figure to
    represent the metamodel in `figure_dir` (requires GraphViz). If
    the syntax is correct and `show_model` is True, also produce a
    figure for the model structure.

    """
    source_path = Path(filemodel)
    metapath = Path(metamodel)
    if not metapath.exists():
        print('ERROR, metamodel file not found: %s' % (metapath, ))
        sys.exit(-1)
    meta = metamodel_from_file(metapath)
    if view_meta:
        meta_output = Path(params.figure_dir,
                           'meta_' + metapath.name).with_suffix('.dot')
        metamodel_export(meta, meta_output)
        figname = str(meta_output.with_suffix('.' + params.img_format))
        os.system("dot -T%s %s > %s" % (params.img_format,
                                        meta_output, figname))
        print('Produced Metamodel figure:', figname)

    with open(source_path) as f:
        content = f.read()

    normalized = yaml.dump(yaml.load(content), default_flow_style=False)
    with open('tmp.yaml', 'w') as f:
        print(normalized, file=f)
    model_check = meta.model_from_str(normalized)
    if view_model:
        model_path = Path(params.figure_dir,
                          'model_%s' % (source_path.name, )).with_suffix('.dot')
        model_export(model_check, model_path)
        figname = str(model_path.with_suffix('.' + params.img_format))
        os.system("dot -T%s %s > %s" % (params.img_format, model_path, figname))
        print('Produced Model figure:', figname)
    Path('tmp.yaml').unlink()
    print('File %s complies with Emulsion syntax' % (filemodel,))


def not_implemented(_):
    """Default behavior for unimplemented features.

    """
    print('Feature not implemented in this model.')
    sys.exit(0)

def set_seed(params, seed=None, show=False):
    """Initialize the numpy's Random Number Generator, either with the
    specified seed, or with a seed calculated from current time and
    process ID.

    """
    if seed is None:
        params.seed = int(os.getpid() + time.time())
    else:
        params.seed = int(seed)
    np.random.seed(params.seed)
    if show:
        print('RANDOM SEED:', params.seed)


def init_main_level(params):
    """Initialize the upper simulation level, in charge of making all
    sub-levels work properly.

    """
    if params.level not in params.model.levels:
        print('ERROR, level %s not found' % (params.level, ))
        sys.exit(-1)
    module_name = params.model.levels[params.level]['module']
    class_name = params.model.levels[params.level]['class_name']
    try:
        params.target_agent_class = load_class(module_name,
                                               class_name=class_name)[0]
    except AttributeError:
        print('ERROR, agent class not found for level %s: %s.%s' %
              (params.level, module_name, class_name))
        sys.exit(-1)
    except ModuleNotFoundError:
        print('ERROR, module not found for level %s: %s' %
              (params.level, module_name))
        sys.exit(-1)

def main(args=None):
    """Run EMuLSion's main program according to the command-line
    arguments.

    """
    if args is None:
        args = docopt(__doc__, version=get_version())
    params = StateVarDict()
    params.model = EmulsionModel(filename=args['MODEL'])
    params.nb_simu = int(args['--runs'])
    params.stochastic = not args['--deterministic']
    params.level = args['--level']

    params.output_dir = Path(args['--output-dir'])
    params.figure_dir = Path(args['--figure-dir'])
    params.img_format = args['--format']
    if not params.output_dir.exists():
        params.output_dir.mkdir(parents=True)
    if not params.figure_dir.exists():
        params.figure_dir.mkdir(parents=True)
    params.output_dir = str(params.output_dir)

    params.stock_agent = False
    params.keep_history = False

    if args['--param']:
        change_parameters(params, args['--param'])

    if args['--time']:
        params.steps = int(args['--time'])
    elif 'total_duration' in params.model.parameters:
        params.steps = int(np.ceil(params.model.get_value('total_duration') \
                                   / params.model.delta_t))
    else:
        params.steps = 100

    set_seed(params, seed=args['--seed'], show=args['--show-seed'])

    if args['--echo']:
        print(args)
        sys.exit(0)

    if args['--view-machines']:
        view_machines(params)

    if args['check']:
        check_model(params, args['MODEL'], args['--metamodel'],
                    args['--view-meta'], args['--view-model'])
    elif args['generate']:
        generate_model(params)
    elif args['run']:
        init_main_level(params)
        run_model(params)
        if args['--plot']:
            plot_outputs(params)
    elif args['show']:
        show_parameters(params)
    elif args['plot']:
        plot_outputs(params)
    elif args['change']:
        not_implemented(params)
    elif args['sensitivity']:
        not_implemented(params)
    else:
        return params


################################################################
#                  _
#                 (_)
#  _ __ ___   __ _ _ _ __
# | '_ ` _ \ / _` | | '_ \
# | | | | | | (_| | | | | |
# |_| |_| |_|\__,_|_|_| |_|
#
################################################################

if __name__ == '__main__':
    main()
