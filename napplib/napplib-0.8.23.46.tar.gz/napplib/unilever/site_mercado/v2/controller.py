# build-in imports
import json
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
		All functions will return a requests.Response.
		#* for more information about unilever APIs: https://caioinovaunilever.bitbucket.io/erp/recent/
		]

	Args:
		environment		(Environment): [The environment for making requests.].
		client_token 			(str): [The Integrator fixed token.].
		integrator_token 		(str): [The Seller fixed token.].
		debug 		 (bool, optional): [Parameter to set the display of DEBUG logs.]. Defaults to False.

	Raises:
		TypeError: [If the client_token is not valid or empty, it will raise a TypeError.]
		TypeError: [If the integrator_token is not valid or empty, it will raise a TypeError.]
		TypeError: [If the environment is not valid, it will raise a TypeError.]
	"""
	environment		: Environment
	client_token	: str
	integrator_token: str
	debug			: bool	= False

	def __post_init__(self):
		level = 'INFO' if not self.debug else 'DEBUG'
		LoggerSettings(level=level)

		if not self.client_token and isinstance(self.client_token, str):
			raise TypeError(f'value provided for client_token is invalid or empty, please provide valid client_token. [client_token: {self.client_token}]')
		if not self.integrator_token and isinstance(self.integrator_token, str):
			raise TypeError(f'value provided for integrator_token is invalid or empty, please provide valid integrator_token. [integrator_token: {self.integrator_token}]')
		if not isinstance(self.environment, Environment):
			raise TypeError(f'please enter a valid environment. environment: {self.environment}')

		self.headers = {'Content-Type': 'application/json'}

		auth_resp = self.__authorization()
		self.token = auth_resp.json()['token']
		# self.token = self.__check_token()

		self.headers.update({'Authorization': f'Basic {self.token}'})

	def __check_token(self):
		# TODO this function will check the token, whether it exists on the hub or has expired.
		# TODO if not exists, self.__authenticate and send this new token for HUB, return token
		# TODO if exist, check expiration_time.
		# TODO if not expired, return token
		# TODO if expired, self.__authenticate and update token on the HUB, return token
		# auth_resp = self.__authorization()
		# token = auth_resp.json()['token']
		# return token
		raise NotImplementedError()

	@AttemptRequests(success_codes=[200])
	def __authorization(self):
		auth = {'clientToken': self.client_token, 'integratorToken': self.integrator_token}
		return requests.post(f'{self.environment.value}/auth', headers=self.headers, data=json.dumps(auth))

	@AttemptRequests(success_codes=[200])
	def post_product(self, products:UnileverProductList):
		return requests.post(f'{self.environment.value}/products', headers=self.headers, data=unpack_payload_dict(products,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def post_product_stock(self, product_stock:UnileverProductStockList):
		return requests.post(f'{self.environment.value}/productstock', headers=self.headers, data=unpack_payload_dict(product_stock,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def post_product_price(self, product_price:UnileverProductPriceList):
		return requests.post(f'{self.environment.value}/productprice', headers=self.headers, data=unpack_payload_dict(product_price,remove_null=True))
