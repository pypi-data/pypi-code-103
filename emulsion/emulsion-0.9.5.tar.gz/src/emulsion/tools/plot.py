"""A Python implementation of the EMuLSion framework.
(Epidemiologic MUlti-Level SImulatiONs).

Plotting tools...

"""

from   pathlib                      import Path

import pandas                       as pd
import numpy                        as np

from   ggplot                       import *

def build_state_plot(df, cols, machine, model, y='qty', group='state'):
    """Return a ggplot object based on the representation of the states in
    the dataframe, with the associated colors (which must follow the
    alphabetical order of states).

    """
    alpha = max(1 /np.sqrt(1 + df.simu_id.max()), 0.05)
    if 'population_id' in df.columns:
        plot = ggplot(aes(x='step', y=y, color=group, alpha='simu_id'),
                      data=df) +\
                      facet_wrap('population_id') +\
                      geom_line(alpha=alpha) +\
                      xlab('Time (steps)') + ylab('Number of animals') +\
                      ggtitle('Evolution of %s (%s)' % (machine.replace('_', ' '),
                                                        model))
    else:
        plot = ggplot(aes(x='step', y=y, color=group, alpha='simu_id'),
                      data=df) +\
                      geom_line(alpha=alpha) +\
                      xlab('Time (steps)') + ylab('Number of animals') +\
                      ggtitle('Evolution of %s (%s)' % (machine.replace('_', ' '),
                                                        model))
    if cols:
        plot += scale_color_manual(values=cols)
    return plot

def plot_outputs(params):
    """Read outputs from previous runs and plot the corresponding
    figures. In the `params` dictionary, `output_dir` is expected to
    contain a `counts.csv` file; `figure_dir` is where the plot is
    saved.

    """
    countpath = Path(params.output_dir, 'counts.csv')
    if not countpath.exists():
        print('ERROR, output file not found: %s' % (countpath, ))
        sys.exit(-1)
    model = params.model
    df = pd.read_csv(countpath)
    vars = ['simu_id', 'step', 'level', 'agent_id']
    if 'population_id' in df.columns:
        vars.append('population_id')
    vals = []
    for sm_name, state_machine in model.state_machines.items():
        col_dict = state_machine.state_colors
        col_dict.update(population="black")
        states, cols = zip(*sorted(col_dict.items()))
        vals += states
        df2 = pd.melt(df, id_vars=vars, value_vars=states,
                      var_name='state', value_name='qty')
        build_state_plot(df2, cols, sm_name, model.model_name).show()
        figpath = Path(params.figure_dir,
                       model.model_name + '_' + sm_name + '.png')
        plot = build_state_plot(df2, cols, sm_name, model.model_name)
        plot.save(str(figpath))
        print('Saved figure %s' % (figpath, ))
    extras = [variable for variable in df.columns if variable not in vars + vals]
    if extras:
        df2 = pd.melt(df, id_vars=vars, value_vars=extras)
        build_state_plot(df2, [], 'Additional variables', model.model_name,
                         y='value', group='variable').show()
        figpath = Path(params.figure_dir,
                       model.model_name + '_extras.png')
        plot = build_state_plot(df2, [], 'Additional variables',
                                model.model_name, y='value', group='variable')
        plot.save(str(figpath))
        print('Saved figure %s' % (figpath, ))
