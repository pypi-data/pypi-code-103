"""Dairy cow QFever disease model.
IBM, stochastic model
Script for within-herd model sensitivity analysis

Author: Yu-Lin Huang

This code is based on the simplified conceptual model by
Aurélie Coulcoul.

"""

import sys
import time
import numpy as np
import pandas as pd

from   pathlib                                  import Path
from   argparse                                 import ArgumentParser
from   emulsion.model                           import EmulsionModel
from   emulsion.tools.state                     import StateVarDict
from   emulsion.tools.parser                    import EmulsionParser
from   emulsion.tools.simulation                import Simulation, MultiSimulation, SensitivitySimulation
from   emulsion.tools.parallel                  import parallel_multi, parallel_sensi
from   simplified_agents                        import QfeverHerd, QfeverMetaPop1D, QfeverFinister2012, QfeverFinister2005

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
)

if __name__ == '__main__':
    version = 'v2.4.2.1'
    parser = EmulsionParser(DEFAULT_PARAM, version=version)

    # define extra line command arguments
    # parser.add_argument('-WH','--within-herd', 
    #                     action='store_true',
    #                     dest='within_herd',
    #                     help='within herd study (-WH: Within Herd)')
    parser.add_argument('-s', '--sensitivity',
                        # action='store_true',
                        dest='sensitivity',
                        help='sensitivity study')
    parser.add_argument('-V', '-vaccinate',
                        nargs=2,
                        metavar=('scenario', 'coverage'),
                        dest='vaccination',
                        help='vaccination study')
    parser.add_argument('--parallel',
                        dest='nb_proc',
                        help='run with multi cpu core')
    parser.add_argument('--output-dir',
                        dest='dir',
                        help='Set directory name (Just the name, not full path) in the QFever output')   
    parser.do_parsing()
    # contribute_distribution(parser.parameters)

    # create new parameters updated
    param = parser.parameters
    # extra parse arguments
    args = parser.parse_args()

    # Define path for output
    output_dir = Path('outputs/qfever')
    # if args.within_herd:
    output_dir = Path(output_dir, 'within_herd')
    # elif args.inter_test:
    #     output_dir = Path(output_dir, 'inter_herd_test')
    # elif args.inter_herd:
    #     output_dir = Path(output_dir, 'inter_herd')
    # elif args.inter_herd_ten_years:
    #     output_dir = Path(output_dir, 'inter_herd_ten_years')
    
    output_dir = Path(output_dir, version)
    
    # Set sensitivity scenarios
    if args.sensitivity:
        output_dir = Path(output_dir, 'sensitivity')
        # model = EmulsionModel(filename=DEFAULT_PARAM['model_path'])
        # sensitivity_default_value = model.get_value(args.sensitivity)
        # df_sensitivity = pd.DataFrame({args.sensitivity: sensitivity_default_value*np.array([1.1, 0.9, 1.25, 0.75])} )
        df = pd.read_csv('data/qfever/fast_scenario/within_herd/fast{}.csv'.format(args.sensitivity))


    if args.dir:
        output_dir = Path(output_dir, args.dir)

    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    nb_proc = 1
    if args.nb_proc:
        nb_proc = int(args.nb_proc)

    # setup model (initialization)

    # if args.within_herd:
    if args.sensitivity:
        simu_param = StateVarDict(nb_simu=50,
                                  steps=52*5+1,
                                  TargetAgentClass=QfeverHerd,
                                  stock_agent=False, 
                                  keep_history=False,
                                  output_dir=str(output_dir),
                                  df=df)
        simu_param.update(DEFAULT_PARAM)
        # df = pd.DataFrame({'init_pop': [20+30*x for x in range(9)]})
        if nb_proc>1:
            parallel_sensi(TargetSimulationClass=SensitivitySimulation, nb_proc=nb_proc, **simu_param)
        else:
            sensi = SensitivitySimulation(**simu_param)
            sensi.run()

        # end = time.perf_counter()
        # print('Simulation finished in {:.2f} s'.format(end-start), '\twith {} process'.format(nb_proc))
        
        # sensi = SensitivitySimulation(df=df, **simu_param)
        # sensi.run()
    else:
        start = time.perf_counter()
        
        simu_param = StateVarDict(nb_simu=50,
                                  steps=300,
                                  TargetAgentClass=QfeverHerd, 
                                  output_dir=str(output_dir))
        simu_param.update(DEFAULT_PARAM)
        if nb_proc>1:
            parallel_multi(TargetSimulationClass=MultiSimulation, nb_proc=nb_proc, **simu_param)
        else:
            multi_simu = MultiSimulation(**simu_param)
            multi_simu.run()
            multi_simu.write_dot()
            # multi_simu.counts_to_csv()

        end = time.perf_counter()
        print('Simulation finished in {:.2f} s'.format(end-start), '\twith {} process'.format(nb_proc))
    # elif args.inter_herd:
    #     # start = time.perf_counter()
    #     if args.sensitivity:
    #         simu_param = StateVarDict(nb_simu=30,
    #                                   model_path = 'config/qfever/qfever-yulin.yaml',
    #                                   steps=52,
    #                                   stock_agent = False,
    #                                   TargetAgentClass=QfeverFinister2012, 
    #                                   output_dir=str(output_dir))
    #         # df = pd.DataFrame({'zeta': [0.36, 0.38, 0.37]})
    #         sensi = SensitivitySimulation(df=df_sensitivity, **simu_param)
    #         sensi.run()

    #     else:    
    #         simu_param = StateVarDict(nb_simu=50,
    #                                   model_path = 'config/qfever/qfever-yulin.yaml',
    #                                   steps=52,
    #                                   stock_agent = False,
    #                                   TargetAgentClass=QfeverFinister2012, 
    #                                   output_dir=str(output_dir))
    #         simu = MultiSimulation(**simu_param)
    #         simu.run()

    # elif args.inter_test:
    #     if args.sensitivity:
    #         simu_param = StateVarDict(nb_simu=200,
    #                                   steps=52,
    #                                   TargetAgentClass=WindTestQfever, 
    #                                   stock_agent = False,
    #                                   output_dir=str(output_dir))
    #         simu_param.update(DEFAULT_PARAM)
    #         df = pd.DataFrame({'m': [x/10 for x in range(8)]})
    #         sensi = SensitivitySimulation(df=df, **simu_param)
    #         sensi.run()
    #         sensi.write_dot()
    #         sensi.counts_to_csv()
    #     else:
    #         simu_param = StateVarDict(nb_simu=200,
    #                                   steps=52,
    #                                   stock_agent = False,
    #                                   TargetAgentClass=QfeverMetaPop1D, 
    #                                   output_dir=str(output_dir))
    #         simu_param.update(DEFAULT_PARAM)
    #         multi_simu = MultiSimulation(**simu_param)
    #         multi_simu.write_dot()
    #         multi_simu.run()
    # elif args.inter_herd_ten_years:
    #     if args.sensitivity:
    #         pass
    #     else:
    #         simu_param = StateVarDict(nb_simu=1,
    #                                   steps=52*9,
    #                                   stock_agent = False,
    #                                   TargetAgentClass=QfeverFinister2005, 
    #                                   output_dir=str(output_dir))
    #         simu_param.update(DEFAULT_PARAM)
    #         multi_simu = MultiSimulation(**simu_param)
    #         multi_simu.write_dot()
    #         multi_simu.run()

    # else:
    #     simu_param = StateVarDict(steps=300)
    #     simu_param.update(DEFAULT_PARAM)
    #     simu = Simulation(TargetAgentClass=QfeverHerd, model=EmulsionModel(filename=simu_param['model_path']), **simu_param)

    #     print('Initialization done, starting simulation ({} steps)'.format(simu_param.steps))
    #     start = time.perf_counter()
        
    #     simu.run()

    #     end = time.perf_counter()
    #     print('Simulation finished in {:.2f} s'.format(end-start),
    #           '\t(~ {:.1f} ms per step)'.format((end-start)*1000/simu_param.steps))

