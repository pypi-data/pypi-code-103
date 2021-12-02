# coding=utf-8
import unittest

import pandas as pd

from QuantOPT.constraints.relaxer import RunOpt

quote = pd.read_csv('F:\\Data\\quote\\2021.csv')
stack_price = quote.pivot_table(index='trade_dt', columns='s_info_windcode', values='s_dq_adjclose')
# select
stock_pool = quote['s_info_windcode'].unique().tolist()[:10]
# create covariance
return_matrix = stack_price[stock_pool].pct_change(1)
cov_price = return_matrix.cov()


class MyTestCaseMinVar(unittest.TestCase):
    @property
    def method(self):
        return 'MinVar'

    def test_main_entry_no_instance(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price}
        constraint_param_list = []
        result = RunOpt.run_opt_single(kwargs_data, constraint_param_list, self.method)
        self.assertEqual(result.success, True)

    def test_main_entry_no_instance_test_constr_cls(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price}
        constraint_param_list = []
        from QuantOPT.conf.conf import setting_yaml_path
        result = RunOpt.run_opt_single(kwargs_data, constraint_param_list, self.method, constr_cls=setting_yaml_path)
        self.assertEqual(result.success, True)

    def test_main_entry_no_instance_test_constr_cls_create_instance(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price}
        constraint_param_list = []
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        result = RunOpt.run_opt_single(kwargs_data, constraint_param_list, self.method, constr_cls=constr_cls)
        self.assertEqual(result.success, True)

    def test_main_entry_no_instance_test_constr_cls_instance(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price}
        constraint_param_list = []
        from QuantOPT.constraints.constraints import Constraints
        # constr_cls = create_constraints_holder(setting_yaml_path)
        result = RunOpt.run_opt_single(kwargs_data, constraint_param_list, self.method, constr_cls=Constraints)
        self.assertEqual(result.success, True)

    def test_main_entry_instance(self):
        constraint_param_list = []
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price)
        result = Ro.run_opt(constraint_param_list, slack=False)
        self.assertEqual(result.success, True)

    def test_main_entry_instance_test_constr_cls_instance(self):
        from QuantOPT.constraints.constraints import Constraints
        constraint_param_list = []
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, constr_cls=Constraints)
        result = Ro.run_opt(constraint_param_list, slack=False)
        self.assertEqual(result.success, True)

    def test_main_entry_instance_test_constr_cls_create_instance(self):
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        constraint_param_list = []
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, constr_cls=constr_cls)
        result = Ro.run_opt(constraint_param_list, slack=False)
        self.assertEqual(result.success, True)

    def test_instance_constraint(self):
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 5}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price)
        result = Ro.run_opt(constraint_param_list, slack=False)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack(self):
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.02}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price)
        result = Ro.run_opt(constraint_param_list, slack=True, )
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_constr_cls_instance(self):
        from QuantOPT.constraints.constraints import Constraints
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.02}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, constr_cls=Constraints)
        result = Ro.run_opt(constraint_param_list, slack=True)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_constr_cls_create_instance(self):
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.02}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, constr_cls=constr_cls)
        result = Ro.run_opt(constraint_param_list, slack=True)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_step_length(self):
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.5}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price)
        result = Ro.run_opt(constraint_param_list, slack=True, step_length=0.1)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_constr_cls_create_instance_test_step_length(self):
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.5}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, constr_cls=constr_cls)
        result = Ro.run_opt(constraint_param_list, slack=True, step_length=0.1)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_constr_cls2_create_instance_test_step_length(self):
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.5}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price)
        result = Ro.run_opt(constraint_param_list, slack=True, step_length=0.1, constr_cls=constr_cls)
        self.assertEqual(result.success, True)


class MyTestCaseMaxRiskAdjReturn(unittest.TestCase):
    @property
    def method(self):
        return 'MaxRiskAdjReturn'

    def test_main_entry_no_instance(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price, 'lambda_r': 2, 'portfolio_returns': return_matrix}
        constraint_param_list = []
        result = RunOpt.run_opt_single(kwargs_data, constraint_param_list, self.method)
        self.assertEqual(result.success, True)

    def test_main_entry_no_instance_test_constr_cls(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price, 'lambda_r': 2, 'portfolio_returns': return_matrix}
        constraint_param_list = []
        from QuantOPT.conf.conf import setting_yaml_path
        result = RunOpt.run_opt_single(kwargs_data, constraint_param_list, self.method, constr_cls=setting_yaml_path)
        self.assertEqual(result.success, True)

    def test_main_entry_no_instance_test_constr_cls_create_instance(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price, 'lambda_r': 2, 'portfolio_returns': return_matrix}
        constraint_param_list = []
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        result = RunOpt.run_opt_single(kwargs_data, constraint_param_list, self.method, constr_cls=constr_cls)
        self.assertEqual(result.success, True)

    def test_main_entry_no_instance_test_constr_cls_instance(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price, 'lambda_r': 2, 'portfolio_returns': return_matrix}
        constraint_param_list = []
        from QuantOPT.constraints.constraints import Constraints
        # constr_cls = create_constraints_holder(setting_yaml_path)
        result = RunOpt.run_opt_single(kwargs_data, constraint_param_list, self.method, constr_cls=Constraints)
        self.assertEqual(result.success, True)

    def test_main_entry_instance(self):
        constraint_param_list = []
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=False)
        self.assertEqual(result.success, True)

    def test_main_entry_instance_test_constr_cls_instance(self):
        from QuantOPT.constraints.constraints import Constraints
        constraint_param_list = []
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=False, constr_cls=Constraints)
        self.assertEqual(result.success, True)

    def test_main_entry_instance_test_constr_cls_create_instance(self):
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        constraint_param_list = []
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, lambda_r=2,
                    portfolio_returns=return_matrix, constr_cls=constr_cls)
        result = Ro.run_opt(constraint_param_list, slack=False)
        self.assertEqual(result.success, True)

    def test_instance_constraint(self):
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 5}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=False)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack(self):
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.02}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=True, )
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_constr_cls_instance(self):
        from QuantOPT.constraints.constraints import Constraints
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.02}, 1, 'ineq')]
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price, 'lambda_r': 2, 'portfolio_returns': return_matrix}
        Ro = RunOpt(method=self.method, constr_cls=Constraints, **kwargs_data)
        result = Ro.run_opt(constraint_param_list, slack=True)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_constr_cls_create_instance(self):
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.02}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, constr_cls=constr_cls, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=True)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_step_length(self):
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.5}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=True, step_length=0.1)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_constr_cls_create_instance_test_step_length(self):
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.5}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, constr_cls=constr_cls, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=True, step_length=0.1)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_constr_cls2_create_instance_test_step_length(self):
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.5}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=True, step_length=0.1, constr_cls=constr_cls, )
        self.assertEqual(result.success, True)


class MyTestCaseMaxIR(unittest.TestCase):
    @property
    def method(self):
        return 'MaxIR'

    def test_main_entry_no_instance(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price, 'lambda_r': 2, 'portfolio_returns': return_matrix}
        constraint_param_list = []
        result = RunOpt.run_opt_single(kwargs_data, constraint_param_list, self.method)
        self.assertEqual(result.success, True)

    def test_main_entry_no_instance_test_constr_cls(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price, 'lambda_r': 2, 'portfolio_returns': return_matrix}
        constraint_param_list = []
        from QuantOPT.conf.conf import setting_yaml_path
        result = RunOpt.run_opt_single(kwargs_data, constraint_param_list, self.method, constr_cls=setting_yaml_path)
        self.assertEqual(result.success, True)

    def test_main_entry_no_instance_test_constr_cls_create_instance(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price, 'lambda_r': 2, 'portfolio_returns': return_matrix}
        constraint_param_list = []
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        result = RunOpt.run_opt_single(kwargs_data, constraint_param_list, self.method, constr_cls=constr_cls)
        self.assertEqual(result.success, True)

    def test_main_entry_no_instance_test_constr_cls_instance(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price, 'lambda_r': 2, 'portfolio_returns': return_matrix}
        constraint_param_list = []
        from QuantOPT.constraints.constraints import Constraints
        # constr_cls = create_constraints_holder(setting_yaml_path)
        result = RunOpt.run_opt_single(kwargs_data, constraint_param_list, self.method, constr_cls=Constraints)
        self.assertEqual(result.success, True)

    def test_main_entry_instance(self):
        constraint_param_list = []
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=False)
        self.assertEqual(result.success, True)

    def test_main_entry_instance_test_constr_cls_instance(self):
        from QuantOPT.constraints.constraints import Constraints
        constraint_param_list = []
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=False, constr_cls=Constraints)
        self.assertEqual(result.success, True)

    def test_main_entry_instance_test_constr_cls_create_instance(self):
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        constraint_param_list = []
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, lambda_r=2,
                    portfolio_returns=return_matrix, constr_cls=constr_cls)
        result = Ro.run_opt(constraint_param_list, slack=False)
        self.assertEqual(result.success, True)

    def test_instance_constraint(self):
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 5}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=False)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack(self):
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.02}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=True, )
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_constr_cls_instance(self):
        from QuantOPT.constraints.constraints import Constraints
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.02}, 1, 'ineq')]
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price, 'lambda_r': 2, 'portfolio_returns': return_matrix}
        Ro = RunOpt(method=self.method, constr_cls=Constraints, **kwargs_data)
        result = Ro.run_opt(constraint_param_list, slack=True)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_constr_cls_create_instance(self):
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.02}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, constr_cls=constr_cls, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=True)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_step_length(self):
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.5}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=True, step_length=0.1)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_constr_cls_create_instance_test_step_length(self):
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.5}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, constr_cls=constr_cls, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=True, step_length=0.1)
        self.assertEqual(result.success, True)

    def test_instance_constraint_slack_test_constr_cls2_create_instance_test_step_length(self):
        from QuantOPT.conf.conf import setting_yaml_path
        from QuantOPT.constraints.constraints import create_constraints_holder
        constr_cls = create_constraints_holder(setting_yaml_path)
        # add the count of weight value which is greater than 0 should be 5 or more constraints!
        constraint_param_list = [('general_count_lower_rc', {'bound_value': 10.5}, 1, 'ineq')]
        Ro = RunOpt(method=self.method, stockpool=stock_pool, sigma2=cov_price, lambda_r=2,
                    portfolio_returns=return_matrix)
        result = Ro.run_opt(constraint_param_list, slack=True, step_length=0.05, constr_cls=constr_cls, )
        self.assertEqual(result.success, True)


class MyTestCaseNotExistsModel(unittest.TestCase):
    def test_no_exists_model(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price}
        constraint_param_list = []
        with self.assertRaises(AttributeError):
            result = RunOpt.run_opt_single(kwargs_data, constraint_param_list, 'test')

    def test_no_exists_model2(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price}
        constraint_param_list = []
        with self.assertRaises(AttributeError):
            Ro = RunOpt(method='test', **kwargs_data)
            result = Ro.run_opt(constraint_param_list, )

    def test_no_exists_model_init_check(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price}
        # constraint_param_list = []
        with self.assertRaises(AttributeError):
            Ro = RunOpt(method='test', check=True, **kwargs_data)

    def test_no_exists_model_init_no_check(self):
        kwargs_data = {'stockpool': stock_pool, 'sigma2': cov_price}
        constraint_param_list = []

        Ro = RunOpt(method='test', check=False, **kwargs_data)
        with self.assertRaises(AttributeError):
            result = Ro.run_opt(constraint_param_list, )


if __name__ == '__main__':
    unittest.main()
