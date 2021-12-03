
from ..utils.base_func import split_range
from ._utils import raise_dataobject as rd
from ..validates import Validate
from multiprocessing import cpu_count
from joblib import Parallel, delayed
from collections.abc import Iterable
from itertools import product
import pandas as pd, os
from pathlib import Path

reg_metrics_names = [
    "r2_score",
    "R",
    "rmse",
    "mae",
    "mse"
]

class GridSearch(object):
    
    def __init__(self, n_jobs=0, verbose=True, tmppath=None):

        cpus = cpu_count()
        if isinstance(n_jobs, int) and n_jobs > 0 and n_jobs <= cpus:
            self.n_jobs = n_jobs
        else:
            self.n_jobs = round(cpus * 0.8)
        self.verbose = verbose
        self.parameter_names = None
        self.parameter_types = None
        self.cv = None
        self.task = "reg"
        self.metrics_prefix = None
        self.tmppath = tmppath

    def fit(self, algo, trainobject, testobject=None, cv=5, print_index=10, **products_dict):
        rd(trainobject)
        if testobject is not None:
            rd(testobject)
        self.cv = cv
        if cv is True:
            self.metrics_prefix = "LOO_"
        elif cv is False:
            self.metrics_prefix = "train_"
        elif isinstance(cv, (int, float, )):
            self.metrics_prefix = f"cv{cv}_"
        elif cv == "test":
            self.metrics_prefix = "test_"
        for i, j in products_dict.items():
            if not isinstance(j, Iterable):
                raise Exception(f"parameter {i} is not a iterable")

        self.print_index = int(print_index)

        # if self.tmppath is not None:
        #     if not os.path.exists(self.tmppath):
        #         os.mkdir(self.tmppath)
        #     self.write_str_title = "index, "
        #     for pname in products_dict.keys():
        #         self.write_str_title += f"{pname}, "
            # self.write_str_title += "\n"

        grids = list(product(*products_dict.values()))
        grids = split_range(grids, self.n_jobs)
        self.parameter_names = list(products_dict.keys())
        self.parameter_types = [ type(param_type[0]) for param_type in products_dict.values()]

        results = Parallel(n_jobs=self.n_jobs, verbose=int(self.verbose))(
            delayed(self.work_function)(algo, trainobject, testobject, process_id, params) \
            for process_id, params in enumerate(grids)
        )

        results = pd.concat(results, axis=0)
        self.results = results

        best_mask = self.results.iloc[:, len(products_dict)] == self.results.iloc[:, len(products_dict)].max()
        self.best_result = self.results[best_mask]
        if len(self.best_result) != 1:
            best_mask = self.best_result.iloc[:, len(products_dict)+2] == self.best_result.iloc[:, len(products_dict)+2].max()
            self.best_result = self.best_result[best_mask]
        if len(self.best_result) != 1:
            self.best_result = self.best_result.iloc[:1, :]

        self.best_p = self.best_result.iloc[:1, :len(products_dict)].to_dict("records")[0]

        return self


    def work_function(self, algo, trainobject, testobject, process_id, params):

        grid_result = []

        if self.tmppath is not None:
            tmpfilepath = str(Path(self.tmppath, "tmp"+str(process_id)+".csv"))


        for index, param_set in enumerate(params):
            line_result = []
            line_result_name = []
            model_dict = {}
            pvalues = ""
            for pname, param, ptype in zip(self.parameter_names, param_set, self.parameter_types):
                model_dict.update({pname: ptype(param)})
                line_result.append(param)
                line_result_name.append(pname)
                pvalues += str(param) + ", "

            v = Validate(algo, trainobject, testobject, **model_dict)
            train = v.validate_switch(self.cv)
            if self.task == "reg":
                line_result += [ train[i] for i in reg_metrics_names ]
                line_result_name += [ self.metrics_prefix+i for i in reg_metrics_names ]
                if testobject is not None:
                    test = v.validate_switch("test")
                    line_result += [test[i] for i in reg_metrics_names]
                    line_result_name += [ "test_"+i for i in reg_metrics_names]

            if index == 0:
                if self.tmppath is not None:
                    with open(tmpfilepath, "w") as f:
                        write_str = "index, "
                        write_str += ", ".join(line_result_name)
                        write_str += "\n"
                        f.writelines(write_str)

            if index % self.print_index == 0:
                if self.tmppath is not None:
                    with open(tmpfilepath, "a") as f:
                        write_str = str(index) + ", "
                        write_str += ", ".join([str(i) for i in line_result]) + "\n"
                        f.writelines(write_str)

            grid_result.append(line_result)

        grid_result = pd.DataFrame(grid_result, columns=line_result_name)
        return grid_result
