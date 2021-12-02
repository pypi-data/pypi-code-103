"""Dairy cow QFever disease model.
IBM, stochastic model

Author: Yu-Lin Huang

This code is based on the simplified conceptual model by
Aurélie Coulcoul.

"""

import sys
import time
import numpy as np
import pandas as pd

from   pathlib                   import Path
from   argparse                  import ArgumentParser
from   emulsion.model            import EmulsionModel
from   emulsion.tools.state      import StateVarDict
from   emulsion.tools.parser     import EmulsionParser
from   emulsion.tools.simulation import Simulation, MultiSimulation,\
                                        SensitivitySimulation
from   emulsion.tools.parallel   import parallel_multi
from   simplified_agents         import QfeverHerd, QfeverMetaPop1D,\
                                        QfeverFinister2012, QfeverFinister2005

DEFAULT_PARAM = StateVarDict(
    model_path = 'config/qfever/qfever-yulin.yaml',
    init_pop=50,
    annual_renew_prop=0.355,
    culling_proba_0 = 0.0057,
    culling_proba_1 = 0.0052,
    culling_proba_2 = 0.0065,
    culling_proba_3 = 0.0067,
    culling_proba_4 = 0.0161,
    culling_proba_5 = 0.0161,
    culling_proba_6 = 1,
    dist_parity_0 = 0.337,
    dist_parity_1 = 0.252,
    dist_parity_2 = 0.173,
    dist_parity_3 = 0.110,
    dist_parity_4 = 0.088,
    dist_parity_5 = 0.040,

    nb_simu=10,
    steps=52,
    stock_agent = False,
    keep_history=False,
)

if __name__ == '__main__':
    version = 'v2.4.2.1'
    parser = EmulsionParser(DEFAULT_PARAM, version=version)

    # define extra line command arguments
    parser.add_argument('-BH', '--inter-herd',
                        action='store_true',
                        dest='inter_herd',
                        help='Between herd study for 2012-2013 in Finister')
    parser.add_argument('-BH10', '--inter-herd-ten-years',
                        action='store_true',
                        dest='inter_herd_ten_years',
                        help='Between herd study for 2005-2013 in Finister (please check number of time steps)')
    parser.add_argument('-T', '--inter-test',
                        action='store_true',
                        dest='inter_test',
                        help='Test the between herd model (wind model) in a one dimension set up')
    parser.add_argument('-WH','--within-herd',
                        action='store_true',
                        dest='within_herd',
                        help='within herd study (-WH: Within Herd)')
    parser.add_argument('-s', '--sensitivity',
                        # action='store_true',
                        dest='sensitivity',
                        help='Sensitivity study for just one parameter (automatically varies target parameter value by\
                              10 and 25 percent). For advanced study, please check out qfever_sensitivity.py file')
    parser.add_argument('-V', '-vaccinate',
                        nargs=2,
                        metavar=('scenario', 'coverage'),
                        dest='vaccination',
                        help='vaccination study')
    parser.add_argument('--parallel',
                        dest='nb_proc',
                        help='run with multi cpu core')
    parser.add_argument('--output-name',
                        dest='dir',
                        help='Set directory name (Just the name, not full path) in the QFever output')
    parser.do_parsing()
    # contribute_distribution(parser.parameters)

    # create new parameters updated
    params = parser.parameters
    # extra parse arguments
    args = parser.parse_args()

    # Define path for output
    output_dir = Path('outputs/qfever')
    if args.within_herd:
        output_dir = Path(output_dir, 'within_herd')
    elif args.inter_test:
        output_dir = Path(output_dir, 'inter_herd_test')
    elif args.inter_herd:
        output_dir = Path(output_dir, 'inter_herd')
    elif args.inter_herd_ten_years:
        output_dir = Path(output_dir, 'inter_herd_ten_years')

    bool_real_simulation = args.within_herd or \
                           args.inter_test  or \
                           args.inter_herd  or \
                           args.inter_herd_ten_years

    if bool_real_simulation:
        output_dir = Path(output_dir, version)

    # Set sensitivity scenarios
    if args.sensitivity:
        output_dir = Path(output_dir, 'sensitivity')
        model = EmulsionModel(filename=DEFAULT_PARAM['model_path'])
        sensitivity_default_value = model.get_value(args.sensitivity)
        df_sensitivity = pd.DataFrame({args.sensitivity: sensitivity_default_value*np.array([1.1, 0.9, 1.25, 0.75])} )


    if args.dir:
        output_dir = Path(output_dir, args.dir)
    elif bool_real_simulation:
        output_dir = Path(output_dir, 'base_model')

    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    nb_proc = 1
    if args.nb_proc:
        nb_proc = int(args.nb_proc)

    # setup model (initialization)

    if args.within_herd:
        if args.sensitivity:
            simu_param = StateVarDict(target_agent_class=QfeverHerd,
                                      output_dir=str(output_dir))
            params.update(simu_param)
            # df = pd.DataFrame({'init_pop': [20+30*x for x in range(9)]})
            sensi = SensitivitySimulation(df=df_sensitivity, **params)
            sensi.run()
        else:
            start = time.perf_counter()

            simu_param = StateVarDict(target_agent_class=QfeverHerd,
                                      output_dir=str(output_dir))
            params.update(simu_param)
            if nb_proc>1:
                parallel_multi(target_simulation_class=MultiSimulation, nb_proc=nb_proc, **params)
            else:
                multi_simu = MultiSimulation(**params)
                multi_simu.run()
                multi_simu.write_dot()
                # multi_simu.counts_to_csv()

            end = time.perf_counter()
            print('Simulation finished in {:.2f} s'.format(end-start), '\twith {} process'.format(nb_proc))
    elif args.inter_herd:
        # start = time.perf_counter()
        if args.sensitivity:
            simu_param = StateVarDict(target_agent_class=QfeverFinister2012,
                                      output_dir=str(output_dir))
            params.update(simu_param)
            # df = pd.DataFrame({'zeta': [0.36, 0.38, 0.37]})
            sensi = SensitivitySimulation(df=df_sensitivity, **params)
            sensi.run()

        else:
            simu_param = StateVarDict(target_agent_class=QfeverFinister2012,
                                      output_dir=str(output_dir))
            params.update(simu_param)
            simu = MultiSimulation(**params)
            simu.run()

    elif args.inter_test:
        if args.sensitivity:
            simu_param = StateVarDict(target_agent_class=WindTestQfever,
                                      output_dir=str(output_dir))
            params.update(simu_param)
            df = pd.DataFrame({'m': [x/10 for x in range(8)]})
            sensi = SensitivitySimulation(df=df, **params)
            sensi.run()
            sensi.write_dot()
            sensi.counts_to_csv()
        else:
            simu_param = StateVarDict(target_agent_class=QfeverMetaPop1D,
                                      output_dir=str(output_dir))
            params.update(simu_param)
            multi_simu = MultiSimulation(**params)
            multi_simu.write_dot()
            multi_simu.run()
    elif args.inter_herd_ten_years:
        if args.sensitivity:
            pass
        else:
            simu_param = StateVarDict(target_agent_class=QfeverFinister2005,
                                      output_dir=str(output_dir))
            params.update(simu_param)
            multi_simu = MultiSimulation(**params)
            multi_simu.write_dot()
            multi_simu.run()

    else:
        simu_param = StateVarDict(steps=300)
        params.update(simu_param)
        simu = Simulation(target_agent_class=QfeverHerd,
                          model=EmulsionModel(filename=params['model_path']),
                          save_results=False,
                          **params)

        print('Initialization done, starting simulation ({} steps)'.format(simu_param.steps))
        start = time.perf_counter()

        simu.run()

        end = time.perf_counter()
        print('Simulation finished in {:.2f} s'.format(end-start),
              '\t(~ {:.1f} ms per step)'.format((end-start)*1000/simu_param.steps))
