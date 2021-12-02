import pandas as pd
import os
import numpy as np
import math

from sklearn.decomposition import NMF

from adlinear import pca
from adlinear import utilities as utl
from adlinear import nmfmodel as nmf
from adlinear import testers as tst
from adlinear import imputer as imp
from adlinear import clusterizer as clu
from adlinear import ntfmodel as ntf
from randomgenerators import randomgenerators as rng

import root_path
import dotenv
from pathlib import Path
dotenv.load_dotenv()


if __name__ == "__main__":

    root_path = root_path.get_root_path()

    rd_path = root_path / os.getenv("rd_subpath")
    imputation_paper_path = rd_path / os.getenv("imputation_paper_subpath")

    data_path = imputation_paper_path / os.getenv("data_subpath")

    temp_data_path = data_path / "temp_data/"
    pictures_path = data_path / "Pics"
    out_data_path = imputation_paper_path / "results/"

    if os.getenv("imp_do_brunet", "False").lower() == "true":
        df_brunet = pd.read_csv(data_path / os.getenv("brunet_filename"))
        df_brunet_groups = pd.read_csv(data_path / os.getenv("brunet_grp_filename"))
        df_brunet.loc[:, "Group"] = df_brunet_groups.loc[:, "Group"]
        ngrps_brunet = 3
        ncomp_brunet = 4
        # la colonne d'attribution des groupes
        if ngrps_brunet == 4:
            df_brunet_priors = df_brunet.replace({"Group": {"ALL_B_1": 1,
                                                            "ALL_B_2": 2,
                                                            "ALL_T": 3,
                                                            "AML": 4}})["Group"]
        else:
            df_brunet_priors = df_brunet.replace({"Group": {"ALL_B": 1,
                                                            "ALL_T": 2,
                                                            "AML": 3}})["Group"]

        df_brunet = df_brunet[df_brunet.columns[2:]]
        df_log_brunet = df_brunet - np.nanmin(df_brunet, axis=0)
        df_log_brunet = np.log(1.0 + df_log_brunet)

        nmf_brunet = nmf.NmfModel(mat=df_brunet, name="brunet",
                                  ncomp=ncomp_brunet, regularization="components", leverage="robust", max_iter=200)
        nmf_log_brunet = nmf.NmfModel(mat=df_log_brunet, name="log_brunet",
                                      ncomp=ncomp_brunet, regularization="components", leverage="robust", max_iter=200)

        if os.getenv("imp_do_brunet_test_prop", "False").lower() == "true":
            # df_res_brunet = tst.test_missing_proportion(df_log_brunet, ncomp=ncomp_brunet,
            #                                             name="log_brunet", grp_priors=df_brunet_priors,
            #                                             p_min=0.0, p_max=0.4, p_step=0.02, n_trials=50,
            #                                             do_save_result=True, outpath=out_data_path)

            p_step = 0.05
            n_step = int(0.4 / p_step)
            missing_props = [round(i * p_step, 2) for i in range(n_step)]
            # missing_props = [0]

            clusters_brunet_priors = clu.Clusterizer(method="set_groups",
                                                     groups=df_brunet_priors,
                                                     name="Brunet_3_groups",
                                                     nb_groups=ngrps_brunet)
            clusters_nmf4_grp3 = clu.Clusterizer(method="nmf.kmeans", nb_groups=3, ncomp=4)

            imp_kmeans = imp.Imputer(method="kmeans",
                                     params={"ngroups": 3})
            imp_nmf_proxy = imp.Imputer(method="nmf.proxy",
                                        params={"ncomp": ncomp_brunet,
                                                "nfill_iters": 0})
            imp_snmf_proxy = imp.Imputer(method="snmf.proxy",
                                         params={"ncomp": ncomp_brunet,
                                                 "nblocks": 2,
                                                 "nfill_iters": 0})

            imp_mean = imp.Imputer("mean", params={})

            imputers = [imp_mean, imp_kmeans, imp_nmf_proxy, imp_snmf_proxy]
            # imputers = [imp_mean, imp_kmeans]

            # imp_tester = imp.ImputerTester(mat=df_log_brunet, name="Log_Brunet_MisClass", imputer=imp_mean,
            #                                ref_clst=clusters_brunet_priors, clst=clusters_nmf4_grp3,
            #                                err_func="Misclassifieds")
            # # missing_props = [0, 0.05]
            # for imputer in imputers:
            #     imp_tester.set_imputer(imputer)
            #     imp_tester.run(missing_props, 100)

            # imp_tester.output_results(out_data_path)

            imp_tester = imp.ImputerTester(mat=df_log_brunet, name="Log_Brunet_MSE", imputer=imp_mean,
                                           ref_clst=clusters_brunet_priors, clst=clusters_nmf4_grp3, err_func="MSE")
            for imputer in imputers:
                imp_tester.set_imputer(imputer)
                imp_tester.run(missing_props, 100)

            imp_tester.output_results(out_data_path)

    if os.getenv("imp_do_random", "False").lower() == "true":

        standard_noise = rng.RandomVariable(np.random.normal, 1, 0.05)

        # direct_x_clones, _ = standard_noise.apply_bias(size=[10, 100], min=0.0, max=4.0)
        # biased_x_clones, _ = standard_noise.apply_bias(size=[10, 100], signal_prop=0.1, bias=0.1, min=0.0, max=4.0)

        dict1 = {"Variable": standard_noise,
                 "Signal_prop": 0.10,
                 "Bias": 0.2,
                 "Coeff": 0.01,
                 "Min": -10,
                 "Max": 10
                 }
        dict2 = {"Variable": standard_noise,
                 "Signal_prop": 0.05,
                 "Bias": 0.1,
                 "Coeff": 0.01,
                 "Min": -10,
                 "Max": 10
                 }
        dict3 = {"Variable": standard_noise,
                 "Signal_prop": 0.20,
                 "Bias": -0.2,
                 "Coeff": 0.01,
                 "Min": -10,
                 "Max": 10
                 }
        dict4 = {"Variable": standard_noise,
                 "Signal_prop": 0.40,
                 "Bias": -0.4,
                 "Min": -10,
                 "Max": 10
                 }
        noise = {"Variable": standard_noise,
                 "Signal_prop": 0.0,
                 "Bias": 0.0,
                 "Coeff": 0.01,
                 "Min": 0,
                 "Max": 4
                 }
        var_list = [dict1, dict2, dict3, dict4]
        noise_factor = 0.50
        n_clones = 100
        n_samples = 250
        my_dls = rng.DependentLocalizedSignals(signal_dist=var_list,
                                               non_overlapping_obs=True,
                                               noise_dist=noise,
                                               cloning_mult=n_clones,
                                               n_crossproducts=30,
                                               n_noisecolumns=int(n_clones*noise_factor),
                                               nsamples=250,
                                               lbound=-10,
                                               ubound=10)
        my_dls_name = my_dls.__repr__()
        _ = my_dls()
        df_rnd_samples = my_dls.get_samples()

        rnd_ngroups = len(var_list) + 1
        df_rnd_groups = df_rnd_samples.loc[:, "Group"]
        df_rnd_mat = df_rnd_samples.drop("Group", axis=1)

        p_step = 0.05
        n_step = int(0.4 / p_step)
        missing_props = [round(i * p_step, 2) for i in range(n_step)]
        # missing_props = [0]

        clusters_rnd_priors = clu.Clusterizer(method="set_groups",
                                              groups=df_rnd_groups,
                                              name=f"{my_dls_name}_{rnd_ngroups}_groups",
                                              nb_groups=rnd_ngroups)

        clusters_nmf = clu.Clusterizer(method="nmf.kmeans", nb_groups=rnd_ngroups, ncomp=rnd_ngroups)
        clusters_kmeans = clu.Clusterizer(method="kmeans", nb_groups=rnd_ngroups, ncomp=rnd_ngroups)

        imp_kmeans = imp.Imputer(method="kmeans",
                                 params={"ngroups": rnd_ngroups})
        imp_nmf_proxy = imp.Imputer(method="nmf.proxy",
                                    params={"ncomp": rnd_ngroups,
                                            "nfill_iters": 0})
        imp_nmf_it1_proxy = imp.Imputer(method="nmf.proxy",
                                        params={"ncomp": rnd_ngroups,
                                                "nfill_iters": 1})

        imp_snmf_proxy = imp.Imputer(method="snmf.proxy",
                                     params={"ncomp": rnd_ngroups,
                                             "nblocks": 2,
                                             "nfill_iters": 0})
        imp_snmf_it1_proxy = imp.Imputer(method="snmf.proxy",
                                         params={"ncomp": rnd_ngroups,
                                                 "nblocks": 2,
                                                 "nfill_iters": 1})

        imp_nmf_fills = imp.Imputer(method="nmf.proxy", params={"ncomp": rnd_ngroups, "nfill_iters": 4})
        imp_snmf_proxy_fills = imp.Imputer(method="snmf.proxy",
                                           params={"ncomp": rnd_ngroups, "nblocks": 2, "nfill_iters": 4})
        imp_mean = imp.Imputer("mean", params={})

        imputers = [[imp_mean, clusters_kmeans],
                    [imp_kmeans, clusters_kmeans],
                    [imp_snmf_proxy, clusters_kmeans],
                    [imp_snmf_proxy, clusters_nmf]
                    ]

        # imputers = [[imp_mean, clusters_kmeans]]
        # imputers = [[imp_kmeans, clusters_kmeans]]

        imp_tester = imp.ImputerTester(mat=df_rnd_mat, name=my_dls_name, imputer=imp_mean, ref_clst=clusters_rnd_priors,
                                       clst=clusters_nmf, err_func="MSE")
        for imputer in imputers:
            imp_tester.set_imputer(imputer[0])
            imp_tester.set_clst(imputer[1])
            imp_tester.run(missing_props, 100)

        imp_tester.output_results(out_data_path)

    if os.getenv("imp_do_ecodata_gans", "False").lower() == "true":

        # localisation du modèle GAN
        path_models = Path('/media/SERVEUR/production/research_and_development/AdFactory/Models/')
        # model_name = '15_09_21_25000_epochs'
        model_name = '20_09_21_10000_epochs'
        path_output_models = path_models / model_name
        critic_name = 'wgan_critic_model'

        eco_feat_list = ['Balance_of_Trade', 'Central_Bank_Balance_Sheet', 'Corruption_Index', 'Food_Inflation',
                         'Foreign_Direct_Investment', 'GDP', 'GDP_Growth_Rate',
                         'Population', 'Terrorism_Index', 'BONDS_10Y_close']
        nb_eco_feat = len(eco_feat_list)
        nb_obs = 500

        # Données d'entrée
        eco_data_path = Path('/media/SERVEUR/production/research_and_development/AdFactory/Data/test_critic_full')
        eco_df = pd.DataFrame(index=range(nb_obs),
                              columns=eco_feat_list,
                               data=np.random.normal(size=[nb_obs, nb_eco_feat]))

        ncomp_eco = 6
        p_step = 0.05
        n_step = int(0.4 / p_step)
        missing_props = [round(i * p_step, 2) for i in range(n_step)]
        imp_kmeans = imp.Imputer(method="kmeans",
                                 params={"ngroups": ncomp_eco})
        imp_nmf_proxy = imp.Imputer(method="nmf.proxy",
                                    params={"ncomp": ncomp_eco,
                                            "nfill_iters": 0})
        imp_snmf_proxy = imp.Imputer(method="snmf.proxy",
                                     params={"ncomp": ncomp_eco,
                                             "nblocks": 2,
                                             "nfill_iters": 0})
        clusters_kmeans = clu.Clusterizer(method="kmeans", nb_groups=ncomp_eco, ncomp=ncomp_eco)

        imputers = [[imp_kmeans, clusters_kmeans],
                    [imp_snmf_proxy, clusters_kmeans],
                    ]

        imp_tester = imp.ImputerTester(mat=eco_df, name="Trading_eco", imputer=imp_kmeans, ref_clst=None, clst=None,
                                       err_func="GAN_critic", critic_path=path_output_models, critic_name=critic_name)

        p_step = 0.05
        n_step = int(0.4 / p_step)
        missing_props = [round(i * p_step, 2) for i in range(n_step)]

        file_list = [f"df_{str(1000+i)[1:4]}.csv" for i in range(1, 101)]
        i_choice = range(5)
        for i in i_choice:
            mat = pd.read_csv(eco_data_path / file_list[i])
            mat = mat.drop(["Date", "Countries"], axis=1)
            imp_tester.set_mat(mat)
            imp_tester.set_name(file_list[i])
            for imputer in imputers:
                imp_tester.set_imputer(imputer[0])
                clusterizer = imputer[1]
                score_opt, scores = clu.clusterizer_optimize(clusterizer, mat)
                imp_tester.set_clst(clusterizer)

                imp_tester.run(missing_props, 100)

        imp_tester.output_results(out_data_path)

        pass
