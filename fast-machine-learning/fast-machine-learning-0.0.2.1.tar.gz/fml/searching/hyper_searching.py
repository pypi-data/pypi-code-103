
from ..descriptors import HOIP
from hyperopt import fmin, hp, tpe, STATUS_OK
from ..data import DataObject

class HOIPHyperSearchingWithVotingRegressor(object):

    def __init__(self, rounds=100, verbose=False, verbose_2=False):
        self.rounds = rounds
        self.verbose = verbose
        self.verbose_2 = verbose_2
        self.formulars = []
        self.trials = []
        self.descriptor_names = None

    def fit_with_full_range(self, votingmodel, formular_info, targted_value, criterion, site_counts=[2, 2, 1], ratio_digit=3):

        """
        formular_info = [
            ["FA", "MA", ...] # atoms in A site
            ["Pb", "Sn", ...] # atoms in B site
            ["Cl", "Br", "I"] # atoms in C site
        ]
        site_counts = [2, 2, 1]
        """
        space = {}

        for site, site_info, site_count in zip(["A", "B", "C"], formular_info, site_counts):
            atom_info = {}
            ratio_info = {}
            if site == "C":
                max_ratio = 2.999
            else:
                max_ratio = 0.999
            for site_i in range(1, site_count+1):
                atom_name = f"{site.lower()}{site_i}"
                ratio_name = f"r{atom_name}"
                atom_info.update({
                    atom_name: hp.choice(atom_name, site_info)
                })
                ratio_info.update({
                    ratio_name: hp.uniform(ratio_name, 0.001, max_ratio)
                })
            space[site] = {
                "atoms": atom_info,
                "ratios": ratio_info,
            }
        def f(params):
            if self.verbose:
                print(params)
            formular = []
            formular_name = ""
            for _, site_info in params.items():
                tmp = {}
                ratio_sum = sum(site_info["ratios"].values())
                for atom, ratio in zip(site_info["atoms"].values(), site_info["ratios"].values()):
                    ratio = ratio / ratio_sum
                    if _ == "C":
                        ratio *= 3
                    ratio = round(ratio, ratio_digit)
                    if atom in tmp.keys():
                        tmp[atom] += ratio
                    else:
                        tmp[atom] = ratio
                for atom, ratio in tmp.items():
                    formular_name += atom
                    if ratio != 1:
                        formular_name += str(round(ratio, ratio_digit))
                formular.append(tmp)
            descriptor = HOIP().describe_formular(formular, True)
            data = DataObject(X=descriptor.values.reshape(1, -1), Y=[0], 
                              Xnames=descriptor.index.values, Yname=votingmodel.trainobjects[0].Yname[0])
            pred = votingmodel.predict(data)[0]
            error = abs(pred - targted_value)
            if error < criterion:
                if formular_name not in self.formulars:
                    self.formulars.append(formular_name)
                    self.trials.append([formular_name, pred, error] + descriptor.tolist())
                    if self.verbose_2:
                        print(f"{formular_name}: {pred}")
            if self.descriptor_names is None:
                self.descriptor_names = descriptor.index.values
            return {"loss": error, "status": STATUS_OK}
        fmin(fn=f, space=space, algo=tpe.suggest, max_evals=self.rounds, verbose=self.verbose)
        return self









