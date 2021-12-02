"""Dairy cow QFever disease model.
IBM, stochastic model

Author: Sébastien Picault & Yu-Lin Huang

This code is based on the conceptual model developped by
Aurélie Coulcoul.

"""

import sys
import time
import numpy as np

from   argparse                                 import ArgumentParser
from   emulsion.tools.state                     import StateVarDict
from   emulsion.tools.parser                    import EmulsionParser
from   emulsion.model                           import EmulsionModel
from   emulsion.examples.qfever.simulation      import Simulation


DEFAULT_PARAM = StateVarDict(
    INIT_POPULATION = 50,
    GLOBAL_VACCINATED = 0,
    ADD_VACCINATED = 0,
    ADD_PARITY = 1,
    CULLING_THRESHOLD = 0.85,
    RENEWAL_THRESHOLD = 1.15,
    ANNUAL_RENEW_PROP = 0.355,
    ANNUAL_VACCINATION_WEEK = 15,
    STEPS = 300,
    NB_SIMU = 200,
)
CULLING_PROBAS = [0.0057, 0.0052, 0.0065, 0.0067, 0.0161, 0.0161, 1.]
PARITY_PROBAS  = [0.337, 0.252, 0.173, 0.11, 0.088, 0.04]

def construct_init_herd(path, d_params, init_states = {}, proba = [], simp = None):
    """ Return a initialized herd with a given groupe states and a given 
    probability distribution of parity composition in a normal herd.
    The simp argument precise the simplified model if it is set True.
    """
    get_random_cycle = lambda lc: np.random.randint(0, herd_.lifecycle.get_value(herd_.lifecycle.stateprops[lc]['max_duration']))
    get_max_cycle    = lambda lc: herd_.lifecycle.get_value(herd_.lifecycle.stateprops[lc]['max_duration'])

    herd_ = QfeverHerd(model=EmulsionModel(filename=path),
                       **d_params)

    cows = [Cow(health_state=herd_.disease.states[hs],
                life_cycle=herd_.lifecycle.states[lc],
                parity=np.random.choice(len(proba), p = proba),
                cycle=get_random_cycle(lc) if not(simp) or hs=='S' else get_max_cycle(lc),
                vaccinated=param.GLOBAL_VACCINATED)
            for (hs, lc), quantity in init_states.items()
            for _ in range(quantity)]
    herd_.add_atoms(cows, init=True)
    return herd_

if __name__ == '__main__':
    parser = EmulsionParser(DEFAULT_PARAM, version='stochastic 1.0')

    # define default values
    param_temp = parser.parameters
    
    # define extra line command arguments
    parser.add_argument('-s', '--simplify',
                        action='store_true',
                        dest='simplify',
                        help='Simplified model (developped by Yu-Lin).')
    parser.add_argument('--with-simulator',
                        action='store_true',
                        dest='with_simulator',
                        help='Within-herd study, number of simulation is set by default 200.')
    parser.do_parsing()

    # extra parse arguments
    args = parser.parse_args()
    if args.simplify:
        init_nb = np.random.multinomial(param_temp.INIT_POPULATION-1, [15/55, 40/55])
        INIT_STATES = {('S','NP') : init_nb[0],
                       ('S', 'P') : init_nb[1],
                       ('I+','P') : 1         }

        from   emulsion.examples.qfever.simplified_agents import QfeverHerd, Cow
        param_temp.MODEL_PATH = 'config/qfever/qfever-yulin.yaml'
        param_temp.ADD_LIFESTATE = 'NP'
        param_temp.ADD_PARITY = 0
    else:
        INIT_STATES = {('S', 'PC') : 50,
                       ('I+', 'PC'): 4 }

        from   emulsion.examples.qfever.original_agents   import QfeverHerd, Cow
        param_temp.MODEL_PATH = 'config/qfever/qfever-original.yaml'
        param_temp.ADD_LIFESTATE = 'BP'

    # create new parameters updated
    param = StateVarDict(param_temp,
                         WEEKLY_RENEW_PROBA = 1 - np.power(1 - param_temp.ANNUAL_RENEW_PROP, 1/52))

    # setup model (initialization)
    herd_params = StateVarDict(cullings=CULLING_PROBAS,
                               culling_threshold=param.CULLING_THRESHOLD,
                               init_pop=param.INIT_POPULATION,
                               global_vaccinated=param.GLOBAL_VACCINATED,
                               renew_threshold=param.RENEWAL_THRESHOLD,
                               renew_proba=param.WEEKLY_RENEW_PROBA,
                               parity_proba=PARITY_PROBAS,
                               add_lifestate=param.ADD_LIFESTATE,
                               add_parity=param.ADD_PARITY,
                               add_vacc=param.ADD_VACCINATED,
                               steps=param.STEPS)
    


    if args.with_simulator and args.simplify:
        simu = Simulation(herd_params)

        print('Initialization done, starting simulation ({} steps)'.format(param.STEPS))
        start = time.perf_counter()
        
        simu.run()
    else:
        herd = construct_init_herd(param.MODEL_PATH, herd_params, 
                                   init_states = INIT_STATES,
                                   proba = PARITY_PROBAS,
                                   simp = args.simplify)

        print('Initialization done, starting simulation ({} steps)'.format(param.STEPS))
        start = time.perf_counter()
        for step in range(param.STEPS):
            herd.evolve()

    end = time.perf_counter()
    print('Simulation finished in {:.2f} s'.format(end-start),
          '\t(~ {:.1f} ms per step)'.format((end-start)*1000/param.STEPS))
