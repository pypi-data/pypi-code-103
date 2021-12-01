from freem_bots.random_provider import RandomProvider
from typing import Any, List


class Tools:
	@staticmethod
	def get_random_selection(possibilities: List[Any], random_provider: RandomProvider):
		''' Select from an unweighted set '''
		return random_provider.choose_randomly(possibilities)

	@staticmethod
	def get_random_weighted_selection(possibilities: List[Any], random_provider: RandomProvider):
		''' Select from a weighted set '''

		probability_matrix = []
		subtotal = 0
		for _, possibility in enumerate(possibilities):
			probability_matrix.append(subtotal)
			subtotal += possibility[1]
		maximum_value = probability_matrix[-1] + possibilities[-1][1]
		random_value = random_provider.get_float() * maximum_value
		hit_index = 0
		for i, current_value in enumerate(probability_matrix):
			next_value = maximum_value if i == (len(probability_matrix) - 1) else probability_matrix[i + 1]
			current_value = probability_matrix[i]
			if current_value <= random_value <= next_value:
				hit_index = i
				break
		selected = possibilities[hit_index][0]
		return selected
