from typing import Tuple

from npf.grapher import *
from npf.repository import *
from npf.testie import Testie, SectionScript, ScriptInitException
from npf.types.dataset import Dataset


class Regression:
    def __init__(self, repo: Repository):
        self.repo = repo

    def accept_diff(self, testie, result, old_result):
        result = np.asarray(result)
        old_result = np.asarray(old_result)
        n = testie.reject_outliers(result).mean()
        old_n = testie.reject_outliers(old_result).mean()
        diff = abs(old_n - n) / old_n
        accept = testie.config["acceptable"]
        accept += abs(result.std() * testie.config["accept_variance"] / n)
        return diff <= accept, diff

    def compare(self, testie:Testie, variable_list, all_results: Dataset, build, old_all_results, last_build,
                allow_supplementary=True,init_done=False) -> Tuple[int,int]:
        """
        Compare two sets of results for the given list of variables and returns the amount of failing test
        :param init_done: True if initialization for current testie is already done (init sections for the testie and its import)
        :param testie: One testie to get the config from
        :param variable_list:
        :param all_results:
        :param build:
        :param old_all_results:
        :param last_build:
        :param allow_supplementary:
        :return: the amount of failed tests (0 means all passed)
        """

        if not old_all_results:
            return 0, 0

        tests_passed = 0
        tests_total = 0
        supp_done = False
        r = False
        tot_runs = testie.config["n_runs"] + testie.config["n_supplementary_runs"]
        for v in variable_list:
            tests_total += 1
            run = Run(v)
            results_types = all_results.get(run)
            # TODO : some config could implement acceptable range no matter the old value
            if results_types is None or len(results_types) == 0:
                continue

            need_supp = False
            for result_type, result in results_types.items():
                if run in old_all_results and not old_all_results[run] is None:
                    old_result = old_all_results[run].get(result_type, None)
                    if old_result is None:
                        continue

                    ok, diff = self.accept_diff(testie, result, old_result)
                    r = True
                    if not ok and len(result) < tot_runs and allow_supplementary:
                        need_supp = True
                        break
                elif last_build:
                    if not testie.options.quiet_regression:
                        print("No old values for %s for version %s." % (run, last_build.version))
                    if old_all_results:
                        old_all_results[run] = {}

            if r and need_supp and testie.options.do_test and testie.options.allow_supplementary:
                try:
                    if not testie.options.quiet_regression:
                        print(
                            "Difference of %.2f%% is outside acceptable margin for %s. Running supplementary tests..." % (
                                diff * 100, run.format_variables()))

                    if not init_done:
                        testie.do_init_all(build=build, options=testie.options, do_test=testie.options.do_test)
                        init_done = True
                    variables = v.copy()
                    for late_variables in testie.get_late_variables():
                        variables.update(late_variables.execute(variables, testie))

                    new_results_types, new_kind_results_types, output, err, n_exec, n_err = testie.execute(build, run, variables,
                                                                    n_runs=testie.config["n_supplementary_runs"],
                                                                    allowed_types={SectionScript.TYPE_SCRIPT, SectionScript.TYPE_EXIT})

                    for result_type, results in new_results_types.items():
                        results_types[result_type] += results

                    if not testie.options.quiet_regression:
                        print("Result after supplementary tests done :", results_types)

                    if new_results_types is not None:
                        supp_done = True
                        all_results[run] = results_types
                        for result_type, result in results_types.items():
                            old_result = old_all_results[run].get(result_type, None)
                            if old_result is None:
                                continue
                            ok, diff = self.accept_diff(testie, result, old_result)
                            r = True
                            if ok is False:
                                break
                    else:
                        ok = True
                except ScriptInitException:
                    pass

            if r and len(results_types) > 0:
                if not ok:
                    print(
                        "ERROR: Test %s is outside acceptable margin between %s and %s : difference of %.2f%% !" % (
                            testie.filename, build.version, last_build.version, diff * 100))
                else:
                    tests_passed += 1
                    if not testie.options.quiet_regression:
                        print("Acceptable difference of %.2f%% for %s" % ((diff * 100), run.format_variables()))

        if supp_done and all_results:
            build.writeversion(testie, all_results, allow_overwrite = True)
        return tests_passed, tests_total

    def regress_all_testies(self, testies: List['Testie'], options, history: int = 1, on_finish = None, iserie=0, nseries=1) -> Tuple[Build, List[Dataset]]:
        """
        Execute all testies passed in argument for the last build of the regressor associated repository
        :param history: Start regression at last build + 1 - history
        :param testies: List of testies
        :param options: Options object
        :return: the lastbuild and one Dataset per testies or None if could not build
        """
        repo = self.repo
        data_datasets = []
        kind_datasets = []

        if repo.url:
            build = repo.get_last_build(history=history)
        else:
            build = Build(repo, 'local', result_path=options.result_path )


        nok = 0

        for itestie,testie in enumerate(testies):
            print("[%s] Running testie %s on version %s..." % (repo.name, testie.filename, build.version))
            regression = self
            if repo.last_build:
                try:
                    old_all_results = repo.last_build.load_results(testie)
                    old_kind_all_results = repo.last_build.load_results(testie, kind=True)
                except FileNotFoundError:
                    old_all_results = None
                    old_kind_all_results = None
            else:
                old_all_results = None
                old_kind_all_results = None
            try:
                if on_finish:
                    def early_results(all_data_results, all_kind_results):
                        on_finish(build,(data_datasets + [all_data_results]),(kind_datasets + [all_kind_results]))
                else:
                    early_results = None
                all_results,kind_results, init_done = testie.execute_all(build, prev_results=build.load_results(testie), prev_kind_results=build.load_results(testie, kind=True), options=options,
                                                 do_test=options.do_test, on_finish=early_results, iserie=iserie*len(testies) + itestie,nseries=len(testies)*nseries)

                if all_results is None and kind_results is None:
                    return None, None, None
            except ScriptInitException:
                return None, None, None

            variables_passed, variables_total = regression.compare(testie, testie.variables, all_results, build,
                                                                   old_all_results,
                                                                   repo.last_build,
                                                                   init_done=init_done, allow_supplementary=options.allow_supplementary)
            if variables_passed == variables_total:
                nok += 1
            data_datasets.append(all_results)
            kind_datasets.append(kind_results)
            testie.n_variables_passed = variables_passed
            testie.n_variables = variables_total

        build.writeResults()
        repo.last_build = build

        build.n_passed = nok
        build.n_tests = len(testies)

        return build, data_datasets, kind_datasets
