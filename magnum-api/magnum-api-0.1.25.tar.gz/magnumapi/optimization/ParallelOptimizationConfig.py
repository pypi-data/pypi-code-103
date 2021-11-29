from dataclasses import dataclass
from typing import List
import magnumapi.commons.json_file as json_file

from magnumapi.optimization.OptimizationConfig import OptimizationConfig
from magnumapi.optimization.ObjectiveConfig import ObjectiveConfig
from magnumapi.optimization.OptimizationNotebookConfig import OptimizationNotebookConfig


@dataclass
class ParallelOptimizationConfig(OptimizationConfig):
    """Class for parallel optimization config used for the genetic algorithm.

    Attributes:
       ansys (ParallelAnsysConfig): parallel ansys config

    """
    ansys: "ParallelAnsysConfig"

    def __str__(self) -> str:
        notebooks_str = "\n\n".join(str(notebook) for notebook in self.notebooks)
        objectives_str = "\n\n".join(str(objective) for objective in self.objectives)
        return "input_folder: %s\n" \
               "output_folder: %s\n" \
               "logger_rel_path: %s\n" \
               "n_pop: %d\n" \
               "n_gen: %d\n" \
               "r_cross: %f\n" \
               "r_mut: %f\n" \
               "objectives: \n\n" \
               "%snotebooks: \n\n" \
               "%s \n\n" \
               "ansys: %s" % (self.input_folder,
                              self.output_folder,
                              self.logger_rel_path,
                              self.n_pop,
                              self.n_gen,
                              self.r_cross,
                              self.r_mut,
                              objectives_str,
                              notebooks_str,
                              self.ansys)

    @staticmethod
    def initialize_config(json_path: str) -> "OptimizationConfig":
        """ Static method initializing an optimization config from a json file

        :param json_path: a path to a json file with config
        :return: initialized OptimizationConfig instance
        """
        data = json_file.read(json_path)

        input_folder = data['input_folder']
        output_folder = data['output_folder']
        logger_rel_path = data['logger_rel_path']
        n_pop = data['n_pop']
        n_gen = data['n_gen']
        r_cross = data['r_cross']
        r_mut = data['r_mut']
        objectives = [ObjectiveConfig(**ff) for ff in data['objectives']]
        notebooks = [OptimizationNotebookConfig(**nb) for nb in data['notebooks']]
        ansys = ParallelAnsysConfig(**data['ansys'])

        return ParallelOptimizationConfig(input_folder=input_folder,
                                          output_folder=output_folder,
                                          logger_rel_path=logger_rel_path,
                                          n_pop=n_pop,
                                          n_gen=n_gen,
                                          r_cross=r_cross,
                                          r_mut=r_mut,
                                          objectives=objectives,
                                          notebooks=notebooks,
                                          ansys=ansys)

    def get_weight(self, objective: str) -> float:
        """ Method iterating through the list of objective config, finding a matching name and returning
        corresponding weight.

        :param objective: name of an objective variable
        :return: value of the objective weight
        """
        for config_objective in self.objectives:
            if config_objective.objective == objective:
                return config_objective.weight

        raise KeyError('Objective name %s not present in objective configs.' % objective)

    def get_constraint(self, objective: str) -> float:
        """ Method iterating through the list of objective config, finding a matching name and returning
        corresponding constraint.

        :param objective: name of an objective variable
        :return: value of the objective constraint
        """
        for config_objective in self.objectives:
            if config_objective.objective == objective:
                return config_objective.constraint

        raise KeyError('Objective name %s not present in objective configs.' % objective)


@dataclass
class ParallelAnsysConfig:
    run_dir: str
    n_parallel_runners: int
    n_proc: int
    root_dir: str
    exec_file: str
