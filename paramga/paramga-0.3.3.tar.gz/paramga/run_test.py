import pytest
import numpy as np
from unittest.mock import MagicMock
from paramga.random_helpers import set_seed
from .run import IterationState, Runner, iteration, run, run_iterator


__module_loc__ = __package__ + '.run'


class TestIteration:

    class TestUnitTests:

        @pytest.fixture(autouse=True)
        def _setup(self, mocker):
            # default args
            self.population = 10
            self.parameters = [MagicMock() for _ in range(self.population)]
            self.iteration_state = IterationState(
                self.parameters,
                self.parameters,
                loss=999999,
                lowest_loss=99999,
            )
            self.mock_func_result = 99
            self.mock_func_result_processed = 99.9
            self.func = MagicMock(return_value=self.mock_func_result)
            self.loss_func = MagicMock(side_effect=lambda out,
                                       param: 0 if param == self.parameters[0] else 1)
            self.mutation_conf = {}
            self.input_data = []
            self.parallel = False

            # Mocks
            self.mutated_params = MagicMock()
            self.crossover_params = MagicMock()
            self.mock_output_postprocess = MagicMock(return_value=self.mock_func_result_processed)

            self.mock_mutate_param_state = mocker.patch(
                __module_loc__ + '.mutate_param_state', return_value=self.mutated_params)

            self.mock_param_crossover = mocker.patch(
                __module_loc__ + '.param_crossover', return_value=self.crossover_params)

        def _default_run(self):
            return set_seed(1)(iteration)(
                iteration_state=self.iteration_state,
                func=self.func,
                loss_func=self.loss_func,
                population=self.population,
                mutation_conf=self.mutation_conf,
                input_data=self.input_data,
                process_outputs=self.mock_output_postprocess,
                parallel=self.parallel,
            )

        def test_runs_ok(self):
            self._default_run()

        def test_model_func_is_called(self):
            self._default_run()
            assert self.func.call_count == self.population
            for params in self.parameters:
                self.func.assert_any_call(
                    params,
                    self.input_data,
                )

        def test_output_post_process_called(self):
            self._default_run()
            assert self.mock_output_postprocess.call_count == self.population
            self.mock_output_postprocess.assert_any_call(
                self.mock_func_result,
            )

        def test_loss_func_is_called(self):
            self._default_run()
            assert self.loss_func.call_count == self.population
            self.loss_func.assert_called_with(
                self.mock_func_result_processed,
                self.parameters[-1],
            )

        def test_param_crossover_called(self):
            self._default_run()
            assert self.mock_param_crossover.call_count == self.population
            self.mock_param_crossover.assert_any_call(
                self.parameters[0],
                self.parameters[0],
            )

        def test_should_call_mutate_param_state(self):
            self._default_run()
            assert self.mock_mutate_param_state.call_count == self.population

        def test_returns_updated_state(self):
            out = self._default_run()
            assert out.iterations == self.iteration_state.iterations + 1
            assert out.parameters == [self.mutated_params for _ in range(self.population)]

    class TestFuncTests:

        @pytest.fixture(autouse=True)
        def _setup(self, mocker):
            # default args
            self.population = 10
            self.parameters = [{"foo": 1, "bar": 1} for _ in range(self.population)]
            self.iteration_state = IterationState(
                self.parameters,
                self.parameters,
                loss=999999,
                lowest_loss=99999,
            )
            self.func = lambda params, data: params['foo'] * 2 + params['bar'] * 4
            self.loss_func = lambda output, params: output - 42
            self.max_foo = 10
            self.mutation_conf = {
                "foo": {
                    "type": "float",
                    "min": 1,
                    "max": self.max_foo,
                    "step": 0.1,
                },
                "bar": {
                    "type": "number",
                    "min": 1,
                    "max": 20,
                    "step": 1,
                },
            }
            self.input_data = []
            self.parallel = False

        def _default_run(self):
            return set_seed(1)(iteration)(
                iteration_state=self.iteration_state,
                func=self.func,
                loss_func=self.loss_func,
                population=self.population,
                mutation_conf=self.mutation_conf,
                input_data=self.input_data,
                parallel=self.parallel,
            )

        def test_run_without_error(self):
            self._default_run()

        def test_should_have_reduced_loss(self):
            out = self._default_run()
            assert out.loss < self.iteration_state.loss

        def test_should_have_mutated_parameters(self):
            out = self._default_run()
            assert len(out.parameters) == len(self.parameters)
            assert out.parameters != self.parameters
            assert all(o['foo'] < self.max_foo for o in out.parameters)


class TestRun:

    def demo_state(self):
        return {
            "foo": 10,
            "bar": 360,
        }

    def demo_conf(self):
        return {
            "foo": {
                "type": "number",
                "min": 1,
                "max": 80,
                "step": 8,
            }
        }

    def demo_model(self):
        def model(params, data):
            return sum(data) * params['foo']
        return model

    def demo_process_outputs_func(self):
        def process_outputs(outputs):
            return outputs + 100
        return process_outputs

    def demo_loss_function(self):
        def loss_function(output, params):
            return abs(params['bar'] - output)
        return loss_function

    def demo_data(self):
        return [1, 2, 3, 3]

    def demo_best_params(self):
        return {
            "foo": 40,
            "bar": 360,
        }

    def _default_run(self, **kwargs):
        default_args = dict(
            param_base=self.demo_state(),
            mutation_conf=self.demo_conf(),
            func=self.demo_model(),
            loss_func=self.demo_loss_function(),
            input_data=self.demo_data(),
            population=8,
            tolerance=0.05,
            max_iterations=100,
            verbose=False,
            parallel=False,
        )
        _kwargs = {**default_args, **kwargs}
        return set_seed(1)(run)(**_kwargs)

    def test_simple_run(self):
        iteration_state = self._default_run()
        assert 100 > iteration_state.iterations > 5
        assert iteration_state.best_parameters == self.demo_best_params()

    def test_limited_by_max_iterations(self):
        tolerance = 0.00000001
        iteration_state = self._default_run(max_iterations=5, tolerance=tolerance)
        assert iteration_state.loss > tolerance
        assert iteration_state.iterations == 5
        assert iteration_state.best_parameters != self.demo_best_params()

    def test_running_in_parallel(self):
        tolerance = 0.0001
        iteration_state = self._default_run(
            tolerance=tolerance,
            parallel=True,
        )

        assert 100 > iteration_state.iterations > 5
        assert iteration_state.loss < tolerance
        assert iteration_state.best_parameters == self.demo_best_params()


class TestRunCls:

    def demo_state(self):
        return {
            "foo": 10,
            "bar": 360,
        }

    def demo_conf(self):
        return {
            "foo": {
                "type": "number",
                "min": 1,
                "max": 80,
                "step": 8,
            }
        }

    def demo_model(self):
        def model(params, data):
            return np.array([d * params['foo'] for d in data])
        return model

    def demo_process_outputs(self):
        def process_outputs(outputs):
            return outputs + 10
        return process_outputs

    def demo_loss_function(self):
        def loss_function(output, params):
            return abs(params['bar'] - sum(output) + 40)
        return loss_function

    def demo_data(self):
        return [1, 2, 3, 3]

    def demo_best_params(self):
        return {
            "foo": 40,
            "bar": 360,
        }

    def _default_instance(self, **kwargs):
        default_args = dict(
            param_base=self.demo_state(),
            mutation_conf=self.demo_conf(),
            func=self.demo_model(),
            loss_func=self.demo_loss_function(),
            input_data=self.demo_data(),
            process_outputs=self.demo_process_outputs(),
            population=8,
            max_iterations=100,
            tolerance=0.05,
        )
        return Runner(**{**default_args, **kwargs})

    def test_simple_run(self):
        runner = self._default_instance()
        iteration_state = runner.run().iteration_state
        assert 100 > iteration_state.iterations > 5
        assert iteration_state.best_parameters == self.demo_best_params()

    def test_limited_by_max_iterations(self):
        tolerance = 0.00000001

        runner = self._default_instance(
            tolerance=tolerance,
            max_iterations=5,
        )

        iteration_state = runner.run().iteration_state
        assert iteration_state.loss > tolerance
        assert iteration_state.iterations == 5
        assert iteration_state.best_parameters != self.demo_best_params()

    def test_best_parameters_is_best_from_current_set(self):
        tolerance = 0.00000001
        runner = self._default_instance(
            tolerance=tolerance,
            max_iterations=5,
        )

        iteration_state = runner.run().iteration_state
        assert iteration_state.loss > tolerance
        assert iteration_state.iterations == 5
        assert iteration_state.best_parameters != self.demo_best_params()

    def test_running_in_parallel(self):
        tolerance = 0.00000001
        runner = self._default_instance(
            tolerance=tolerance,
            parallel=True,
        )

        iteration_state = runner.run().iteration_state
        assert 100 > iteration_state.iterations > 5
        assert iteration_state.loss <= tolerance
        assert iteration_state.loss == 0
        assert iteration_state.best_parameters == self.demo_best_params()

    def test_run_as_iterator(self):
        tolerance = 0.05
        runner = self._default_instance(
            tolerance=tolerance,
            parallel=True,
        )

        for iteration_state in iter(runner):
            pass
        assert 100 > iteration_state.iterations > 5
        assert iteration_state.loss <= tolerance

    def test_can_store_iteration_data(self):
        tolerance = 0.05
        runner = self._default_instance(
            tolerance=tolerance,
            parallel=True,
        )
        runner.store_iterations()
        final_state = runner.run().iteration_state
        assert len(runner.history) == final_state.iterations + 1

    # def test_should_store_parameters_in_order(self):
    #     tolerance = 0.05
    #     runner = Runner(
    #         self.demo_state(),
    #         self.demo_conf(),
    #         self.demo_model(),
    #         self.demo_loss_function(),
    #         self.demo_data(),
    #         max_iterations=100,
    #         tolerance=tolerance,
    #         parallel=True,
    #     )
    #     runner.store_iterations()
    #     runner.run().iteration_state
    #     assert runner.initial_parameters == runner.history[0].parameters

    def test_should_plot_loss(self):
        tolerance = 0.001
        runner = self._default_instance(
            tolerance=tolerance,
            parallel=True,
        )
        runner = self._default_instance(
            tolerance=tolerance,
        )
        runner.store_iterations()
        runner.run()
        runner.plot()

    def test_should_plot_param(self):
        tolerance = 0.001
        runner = self._default_instance(
            tolerance=tolerance,
        )
        runner.store_iterations()
        runner.run()
        runner.plot_param('foo')

    def test_should_plot_param_compare(self):
        tolerance = 0.001
        runner = self._default_instance(
            tolerance=tolerance,
        )
        runner.store_iterations()
        runner.run()
        runner.plot_param_compare('foo', 'bar')



    def test_should_plot_observed_compare(self):
        tolerance = 0.001
        runner = self._default_instance(
            tolerance=tolerance,
        )
        runner.store_iterations()
        runner.run().iteration_state
        print(runner.func(runner.iteration_state.best_parameters, runner.input_data))
        observed_data = np.array(runner.input_data)
        runner.plot_compare_with_observed(observed_data)


class TestRunParallelIterator:

    def demo_state(self):
        return {
            "foo": 10,
            "bar": 360,
        }

    def demo_conf(self):
        return {
            "foo": {
                "type": "number",
                "min": 3,
                "max": 80,
                "step": 8,
            }
        }

    def demo_loss_function(self):
        def loss_function(output, params):
            return abs(params['bar'] - output)
        return loss_function

    def demo_data(self):
        return [1, 2, 3, 3]

    def demo_best_params(self):
        return {
            "foo": 40,
            "bar": 360,
        }

    @set_seed(1)
    def test_simple_run(self):
        def demo_model_b(params, data):
            return sum(data) * params['foo']

        model = run_iterator(
            self.demo_state(),
            self.demo_conf(),
            demo_model_b,
            self.demo_loss_function(),
            self.demo_data(),
            max_iterations=100,
            tolerance=0.005,
            verbose=True,
        )
        iterations_state = next(model)
        assert iterations_state.iterations == 1
        assert iterations_state.loss < 99999
