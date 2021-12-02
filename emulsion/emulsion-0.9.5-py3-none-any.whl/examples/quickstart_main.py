"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions defining agents involved for the Quickstart model.

"""

import os
import time
import numpy             as np
import pandas            as pd
import matplotlib.pyplot as plt
import matplotlib.image  as mpimg

from   pathlib                      import Path

from   emulsion.model               import EmulsionModel
from   emulsion.tools.state         import StateVarDict
from   emulsion.tools.parser        import EmulsionParser
from   emulsion.tools.simulation    import MultiSimulation
from   emulsion.examples.quickstart import Herd

DEFAULT_PARAM = StateVarDict(
    model_path = 'config/quickstart.yaml',
    nb_simu=10,
    steps=52,
    stock_agent = False,
    keep_history=False,
)


# def plot_diagram(model, machine_name):
#     #plt.style.use('ggplot')
#     #plt.xkcd()
#     statemachine = model.state_machines[machine_name]

#     fig = plt.figure(figsize=(15,12))
#     # ax0 = plt.subplot2grid((2,2), (0,0), colspan=2)
#     # ax0.imshow(mpimg.imread('outputs/quickstart-%s.png'))
#     # for sp in ax0.spines.values():
#     #     sp.set_visible(False)
#     # ax0.set_axis_off()

#     ax1 = plt.subplot2grid((1, 2), (0, 0))
#     #ax1 = fig.add_subplot(223)
#     ys = np.row_stack([herd.counts[state.name] for state in statemachine.states])
#     cols = [statemachine.graph.node[state.name]['fillcolor']
#             if 'fillcolor' in statemachine.graph.node[state.name]
#             else 'lightgray' for state in statemachine.states]
#     pops=ax1.stackplot(np.arange(STEPS + 1), ys, colors=cols)

#     ax2 = plt.subplot2grid((1, 2), (0, 1))
#     #ax2 = fig.add_subplot(224)
#     for (i, state) in enumerate(statemachine.states):
#         ax2.plot(np.arange(STEPS + 1), herd.counts[state.name], cols[i])
#     #plt.imshow(plt.imread('outputs/sir.svg'))

#     lboxes = []
#     for pop in pops:
#         lboxes.append(plt.Rectangle((0, 0), 1, 1, fc=pop.get_facecolor()[0]))
#     llabs = [state.name for state in statemachine.states]
#     plt.legend(lboxes, llabs, loc="upper left", bbox_to_anchor=[1, 1],
#                ncol=2, shadow=True, title=machine_name.replace('_', ' '), fancybox=True)

#     plt.savefig('img/quickstart-%s.png' % machine_name)
#     plt.show()


if __name__ == '__main__':
    version = 'v0.9'
    parser = EmulsionParser(DEFAULT_PARAM, version=version)

    parser.add_argument('--view-machines', 
                        action='store_true', 
                        dest='view_machines',
                        help='Draw the state machines with Graphviz.')

    # parser.add_argument('--plot', 
    #                     action='store_true', 
    #                     dest='plot',
    #                     help='Plot the population diagrams when finished.')

    # define extra line command arguments
    parser.do_parsing()
    # contribute_distribution(parser.parameters)

    # create new parameters updated
    params = parser.parameters
    # extra parse arguments
    args = parser.parse_args()

    if not parser.parameters.output_dir.exists():
        parser.parameters.output_dir.mkdir(parents=True)

    # setup model (initialization)

            
    start = time.perf_counter()

    simu_param = StateVarDict(TargetAgentClass=Herd, 
                              output_dir=str(args.output_dir))
    params.update(simu_param)
    multi_simu = MultiSimulation(**params)
    multi_simu.run()
    multi_simu.write_dot()
    # multi_simu.counts_to_csv()

    if args.view_machines:
        for name, machine in parser.model.state_machines.items():
            path=Path(args.output_dir, name+'.dot')
            # machine.write_dot(str(path))
            os.system("dot -Tpng %s > %s" % (str(path), str(path.with_suffix('.png'))))

    end = time.perf_counter()
    print('Simulation finished in {:.2f} s'.format(end-start))

    # if args.plot:
    #     plot_diagram(parser.model, 'health_state')
    #     plot_diagram(parser.model, 'life_cycle')
