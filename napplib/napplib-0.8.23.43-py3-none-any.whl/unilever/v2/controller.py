# build-in imports
from dataclasses 	import dataclass
from typing 		import List

# external imports
import requests
from loguru import logger

# project imports
from .utils								import Environment
from napplib.unilever.v2.models.product	import UnileverProductList
from napplib.unilever.v2.models.product	import UnileverProductStockList
from napplib.unilever.v2.models.product	import UnileverProductPriceList
from napplib.utils						import AttemptRequests
from napplib.utils						import unpack_payload_dict
from napplib.utils						import LoggerSettings


@dataclass
class UnileverController:
	"""[This function will handle unilever calls..
		All functions will return a requests.Response.]

	Args:
		environment	(Environment): [The environment for making requests.].
		token 		(str): [The Authorization Token.].
		debug 		(bool, optional): [Parameter to set the display of DEBUG logs.]. Defaults to False.

	Raises:
		TypeError: [If the token is not valid or empty, it will raise a TypeError.]
		TypeError: [If the environment is not valid, it will raise a TypeError.]
	"""
	environment	: Environment
	token		: str
	debug		: bool	= False

	def __post_init__(self):
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)

		if not self.token and isinstance(self.token, str):
			raise TypeError(f'value provided for token is invalid or empty, please provide valid token. [token: {self.token}]')

		if not isinstance(self.environment, Environment):
			raise TypeError(f'please enter a valid environment. environment: {self.environment}')

		self.headers = {'Authorization': f'Basic {self.token}', 'Content-Type': 'application/json'}

	@AttemptRequests(success_codes=[200])
	def post_product(self, products:UnileverProductList):
		return requests.post(f'{self.environment.value}/products', headers=self.headers, data=unpack_payload_dict(products,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def post_product_stock(self, product_stock:UnileverProductStockList):
		return requests.post(f'{self.environment.value}/productstock', headers=self.headers, data=unpack_payload_dict(product_stock,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def post_product_price(self, product_price:UnileverProductPriceList):
		return requests.post(f'{self.environment.value}/productprice', headers=self.headers, data=unpack_payload_dict(product_price,remove_null=True))
