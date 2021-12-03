"""Exports a problem file to a PDDL file according to the input given."""
from pathlib import Path
from typing import NoReturn, List, Dict

from pddl.pddl import Predicate, Type, Problem


class ProblemExporter:
	"""Class that is able to export a domain to a correct PDDL file."""

	@staticmethod
	def write_objects(problem_objects: Dict[str, Type]) -> str:
		"""Writes the definitions of the types according to the PDDL file format.

		:param problem_objects: the objects that are available in the learned domain.
		:return: the formatted string representing the objects in the PDDL problem file.
		"""
		objects_str = "(:objects\n{objects_content}\n)\n"
		objects = []
		for object_name, pddl_type in problem_objects.items():
			objects.append(f"\t{object_name} - {pddl_type.name}")

		return objects_str.format(objects_content="\n".join(objects))

	@staticmethod
	def write_initial_state(initial_state: List[Predicate]) -> str:
		"""Writes the definitions of the types according to the PDDL file format.

		:param initial_state: the objects that are available in the learned domain.
		:return: the formatted string representing the state in the PDDL problem file.
		"""
		state_str = "(:init\n{state_content}\n)\n"
		predicates = ProblemExporter.extract_state_predicates(initial_state)
		return state_str.format(state_content="\n".join(predicates))

	@staticmethod
	def write_goal_state(goal_state: List[Predicate]) -> str:
		"""Writes the definitions of the types according to the PDDL file format.

		:param goal_state: the objects that are available in the learned domain.
		:return: the formatted string representing the state in the PDDL problem file.
		"""
		state_str = "(:goal\n\t(and\n{state_content}\t\n)\n)\n"
		predicates = ProblemExporter.extract_state_predicates(goal_state)
		return state_str.format(state_content="\n".join(predicates))

	@staticmethod
	def extract_state_predicates(state: List[Predicate]) -> List[str]:
		"""Extract the needed problem predicates for the PDDL file representation.

		:param state: the state to write in a PDDL format.
		:return: the strings of containing the state's data.
		"""
		predicates = []
		for predicate in state:
			predicate_objects = [obj[0] for obj in predicate.signature]
			objects_str = " ".join(predicate_objects)
			predicates.append(f"\t({predicate.name} {objects_str})")
		predicates = list(set(predicates))
		return predicates

	def export_problem(self, problem: Problem, export_path: Path) -> NoReturn:
		"""Export the domain object to a correct PDDL file.

		:param problem: the problem object to export to a PDDL file.
		:param export_path: the path to the file that the domain would be exported to.
		"""
		problem_objects = self.write_objects(problem.objects)
		initial_state = self.write_initial_state(problem.initial_state)
		goal_state = self.write_goal_state(problem.goal)
		problem_data = f"(define (problem {problem.name}) (:domain {problem.domain.name})\n" \
					   f"{problem_objects}\n" \
					   f"{initial_state}\n" \
					   f"{goal_state}\n)"

		with open(export_path, "wt") as export_problem_file:
			export_problem_file.write(problem_data)
