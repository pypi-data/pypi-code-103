import random
from typing import Any, List


class RandomProvider:
	def __init__(self) -> None:
		self.random = random.Random()

	def get_float(self) -> float:
		return self.random.random()

	def get_int(self, lower_bound: int, upper_bound: int) -> int:
		return self.random.randint(lower_bound, upper_bound)

	def choose_randomly(self, options: List[Any]) -> Any:
		return self.random.choice(options)
