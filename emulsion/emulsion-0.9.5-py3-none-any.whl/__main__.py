"""Usage:
    emulsion check MODEL [options]
    emulsion generate MODEL
    emulsion run MODEL [options] [(-p KEY=VALUE)...]
    emulsion show MODEL [options] [(-p KEY=VALUE)...]
    emulsion plot MODEL [options]
    emulsion sensitivity MODEL DESIGN [options]
    emulsion change MODEL NEW_MODEL (-p KEY=VALUE)...
    emulsion (-h | --help | --version)

Options:
  check MODEL                     Check the syntactic correctness of the given
                                  MODEL, according to the META-model expressed
                                  as a textX grammar file. If the model is
                                  correct, generate figures to represent the
                                  MODEL structure and (with --show-meta) the
                                  META-model itself.
  generate MODEL                  Generate a skeleton to help writing specific
                                  pieces of code before the model can be run,
                                  and exit.
  run MODEL                       Run simulations based on the specified MODEL
                                  (path to YAML file of the model to run).
  show MODEL                      Print all model parameters and exit.
  plot MODEL                      Plot outputs for specified model (based on
                                  previous runs), save figures and exit.
  sensitivity MODEL DESIGN        Run a sensitivity analysis for the specified
                                  MODEL using the provided experimental DESIGN.
  change MODEL NEW_MODEL          Modify the initial MODEL into a NEW_MODEL
                                  using appropriate options, and exit.
  -r RUNS --runs RUNS             Specify the number of repetitions of the
                                  same model [default: 10].
  -t STEPS --time STEPS           Specify the number of steps to run in each
                                  repetition [default: 100].
  --metamodel META                Specify a metamodel for syntax checking
                                  [default: scripts/emulsion.tx]
  --show-meta                     Output a figure for the meta-model.
  --init INIT_FILE                Speficy a file for initial conditions.
  --scale SCALE                   Specify a scale for running the model.
  --class AGENT                   Specify the top-level agent class (entity of
                                  the highest level) used in the simulation,
                                  e.g. a Herd or a Metapopulation class
                                  [default: emulsion.examples.quickstart.Herd].
  --seed SEED                     Set a seed value for random numbers.
  --show-seed                     Print the seed used for random numbers.
  --output-dir OUTPUT             Specify a directory for simulation outputs
                                  [default: outputs].
  --format FORMAT                 Specify an image format for diagram outputs
                                  [default: png].
  --input-dir INPUT               Specify a directory for simulation inputs
                                  [default: data].
  --xkcd                          Display figures using XKCD style.
  --figure-dir FIG                Specify a directory for graphic outputs
                                  (figures) [default: img].
  --view-machines                 Draw the state machines with Graphviz.
  -h --help                       Display this page and exit.
  --version                       Display version number and exit.
  -p KEY=VALUE --param KEY=VALUE  Change parameter named KEY to the
                                  specified VALUE.
  --test                          Run the simulation in test mode.
"""

import sys
import os
import time
import subprocess
import datetime                     as dt

from   pathlib                      import Path

import yaml
import numpy

from   docopt                       import docopt
from   textx                        import metamodel_from_file
from   textx.export                 import metamodel_export, model_export

from   emulsion.model               import EmulsionModel
from   emulsion.tools.state         import StateVarDict
from   emulsion.tools.misc          import load_class
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
                          for level_desc in model.levels.values()]))
    for module in modules:
        mod_path = Path(src_path, *module.split('.')).with_suffix('.py')
        if mod_path.exists():
            print('WARNING, file %s already exists, ' % str(mod_path,), end='')
            mod_path = mod_path.with_suffix(
                '.py.%s' % (str(dt.datetime.now().timestamp())))
            print('writing in %s instead' % str(mod_path,))
        print('GENERATING CODE SKELETON %s\nFOR MODULE %s' % (str(mod_path),
                                                              module,))
        with open(mod_path, 'w') as f:
            print(model.generate_skeleton(module), file=f)


def run_model(params):
    """Run the model with the specified local parameters.

    """
    multi_simu = MultiSimulation(**params)
    # multi_simu.write_dot()
    start = time.perf_counter()
    multi_simu.run()
    end = time.perf_counter()
    print('Simulation finished in {:.2f} s'.format(end-start))


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
        os.system("dot -T%s %s > %s" % (params.img_format,
                                        str(inpath),
                                        str(outpath)))

def check_model(params, filemodel, metamodel, show_meta=False):
    """Check the syntax of the model according to the grammar specified in
    the metamodel. If the syntax is correct, produce a figure for the
    model structure in `figure_dir`. If `show_meta` is True, also
    produce a figure to represent the metamodel.

    """
    source_path = Path(filemodel)
    metapath = Path(metamodel)
    if not metapath.exists():
        print('ERROR, metamodel file not found:', str(metapath))
        sys.exit(-1)
    meta = metamodel_from_file(metapath)
    if show_meta:
        meta_output = Path(params.figure_dir,
                           'meta_' + metapath.name).with_suffix('.dot')
        metamodel_export(meta, meta_output)
        figname = str(meta_output.with_suffix('.' + params.img_format))
        os.system("dot -T%s %s > %s" % (params.img_format,
                                        str(meta_output), figname))
        print('Produced Metamodel figure:', figname)

    with open(source_path) as f:
        content = f.read()
    normalized = yaml.dump(yaml.load(content), default_flow_style=False)
    with open('tmp.yaml', 'w') as f:
        print(normalized, file=f)
    model_check = meta.model_from_str(normalized)
    model_path = Path(params.figure_dir,
                      'model_' + str(source_path.name)).with_suffix('.dot')
    model_export(model_check, model_path)
    figname = str(model_path.with_suffix('.' + params.img_format))
    os.system("dot -T%s %s > %s" % (params.img_format,
                                    str(model_path),
                                    figname))
    print('Produced Model figure:', figname)
    Path('tmp.yaml').unlink()
    print('File %s complies with Emulsion syntax' % (filemodel,))

def plot_outputs(params, xkcd=False):
    """Read outputs from previous runs and plot the corresponding
    figures. `output_dir` is expected to contain a `counts.csv` file;
    `figure_dir` is where the plot is saved. The `xkcd` option is here
    for fun.

    """
    countpath = Path(params.output_dir, 'counts.csv')
    if not countpath.exists():
        print('ERROR, output file not found:', str(countpath))
        sys.exit(-1)
    import pandas as pd
    import ggplot as gg
    model = params.model
    df = pd.read_csv(countpath)
    for sm_name, state_machine in model.state_machines.items():
        figpath = Path(params.figure_dir,
                       model.model_name + '_' + sm_name + '.png')
        plot = gg.ggplot(gg.aes(x='step'),
                         data=df) +\
                         gg.facet_wrap('simu_id') +\
                         gg.ggtitle('Evolution of ' + sm_name) +\
                         gg.xlab('Time (steps)') +\
                         gg.ylab('Number of animals')
        if xkcd:
            plot += gg.theme_xkcd()
        for state in state_machine.states:
            col = state_machine.graph.node[state.name]['fillcolor']\
                  if 'fillcolor' in state_machine.graph.node[state.name]\
                  else 'lightgray'
            plot += gg.geom_line(gg.aes(y=state.name), color=col)
        plot.save(str(figpath))
        print(plot)

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
    numpy.random.seed(params.seed)
    if show:
        print('RANDOM SEED:', params.seed)

def main():
    """Run EMuLSion's main program according to the command-line
    arguments.

    """
    args = docopt(__doc__, version=get_version())
    params = StateVarDict()
    params.model = EmulsionModel(filename=args['MODEL'])
    params.nb_simu = int(args['--runs'])
    params.steps = int(args['--time'])

    params.output_dir = Path(args['--output-dir'])
    params.figure_dir = Path(args['--figure-dir'])
    params.img_format = args['--format']
    if not params.output_dir.exists():
        params.output_dir.mkdir(parents=True)
    if not params.figure_dir.exists():
        params.figure_dir.mkdir(parents=True)

    module_name, class_name = args['--class'].rsplit('.', 1)
    try:
        target_agent_class = load_class(module_name, class_name=class_name)[0]
    except AttributeError:
        print('ERROR, agent class not found:', args['--class'])
        sys.exit(-1)

    simu_param = StateVarDict(target_agent_class=target_agent_class,
                              output_dir=str(params.output_dir),
                              stock_agent=False,
                              keep_history=False)
    params.update(simu_param)

    if args['--param']:
        change_parameters(params, args['--param'])

    set_seed(params, seed=args['--seed'], show=args['--show-seed'])

    if args['--view-machines']:
        view_machines(params)

    if args['check']:
        check_model(params, args['MODEL'], args['--metamodel'],
                    args['--show-meta'])
    elif args['generate']:
        generate_model(params)
    elif args['run']:
        run_model(params)
    elif args['show']:
        show_parameters(params)
    elif args['plot']:
        plot_outputs(params, xkcd=args['--xkcd'])
    elif args['change']:
        not_implemented(params)
    elif args['sensitivity']:
        not_implemented(params)


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
