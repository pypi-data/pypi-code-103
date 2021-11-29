import os
import tempfile

import numpy as np
import pandas as pd
import petab_MS

from fitmulticell.model import MorpheusModel as morpheus_model
from fitmulticell.PEtab.base import PetabImporter


def test_PEtab_vs_noPEtab():
    """
    Check the the similarity between PEtab problem and regular problem
    in FitMultiCell.
    """

    def simulation_prep(sumstat):
        new_sumstat = {}
        for key, _val in sumstat.items():
            if key == "loc":
                continue
            new_sumstat["condition1__" + key] = sumstat[key]
        return new_sumstat

    def eucl_dist(sim, obs):
        total = 0
        for key in sim:
            if key in ('loc', "IdSumstat__time", "IdSumstat__space.x"):
                continue
            x = np.array(sim[key])
            y = np.array(obs[key])
            if x.size != y.size:
                return np.inf

            total += np.sum((x - y) ** 2)
        return total

    # Regular problem
    file = os.path.normpath(os.getcwd() + os.sep)
    # file = os.getcwd()
    par_map = {
        'rho_a': './Global/System/Constant[@symbol="rho_a"]',
        'mu_i': './Global/System/Constant[@symbol="mu_i"]',
        'mu_a': './Global/System/Constant[@symbol="mu_a"]',
    }
    obs_pars = {
        'rho_a': 0.01,
        'mu_i': 0.03,
        'mu_a': 0.02,
    }
    condition1_obs = str(file + '/doc/example/PEtab_problem_1' + '/Small.csv')
    model_file = str(
        file
        + '/doc/example/PEtab_problem_1'
        + '/ActivatorInhibitor_1D_seed.xml'
    )

    data = pd.read_csv(condition1_obs, sep='\t')
    tmp_dir = tempfile.TemporaryDirectory()
    dict_data = {}
    for col in data.columns:
        dict_data[col] = data[col].to_numpy()
    model = morpheus_model(
        model_file,
        par_map=par_map,
        par_scale="lin",
        executable="morpheus",
        ignore_list=["time", "loc", "space.x"],
        dir=tmp_dir.name,
        ss_post_processing=simulation_prep,
        clean_simulation=False,
    )
    # model = morpheus_model(
    #     model_file, par_map=par_map,
    #     executable="morpheus",
    #     show_stdout=False, show_stderr=True,
    #     raise_on_error=False,
    #     dir=tmp_dir.name,
    #     ignore_list=["time", "loc"],
    #     clean_simulation=False,
    #     ss_post_processing=simulation_prep)
    trajectory = model.sample(obs_pars)

    # PEtab problem
    tmp_dir = tempfile.TemporaryDirectory()
    petab_problem_path = str(
        file + '/doc/example/PEtab_problem_1' + '/ActivatorInhibitor_1D.yaml'
    )
    petab_problem = petab_MS.Problem.from_yaml(petab_problem_path)
    importer = PetabImporter(petab_problem)
    obs_pars_imported = petab_problem.get_x_nominal_dict(scaled=False)
    importer.petab_problem.model_file = (
        file
        + '/doc/example/PEtab_problem_1'
        + '/ActivatorInhibitor_1D_seed.xml'
    )
    petab_model = importer.create_model()
    petab_model.ignore_list = ["time", "loc", "space.x"]
    petab_model.executable = "morpheus"
    petab_model.clean_simulation = False
    petab_model.dir = tmp_dir.name
    petab_model.par_scale = "lin"
    petab_trajectory = petab_model.sample(obs_pars_imported)
    assert (eucl_dist(petab_trajectory, trajectory)) == 0
