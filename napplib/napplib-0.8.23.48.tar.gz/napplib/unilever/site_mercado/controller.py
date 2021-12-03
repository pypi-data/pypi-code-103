import json
from dataclasses 	import dataclass

import requests
from loguru import logger

from .utils				import Environment
from .models.auth		import UnileverSiteMercadoAuth
from .models.product	import UnileverSiteMercadoProductList, UnileverSiteMercadoProductPriceList, UnileverSiteMercadoProductStockList
from napplib.utils		import AttemptRequests, unpack_payload_dict, LoggerSettings


@logger.catch()
@dataclass
class UnileverSiteMercadoController:
	"""[This function will handle unilever calls..
		All functions will return a requests.Response.
		#* for more information about unilever APIs: http://prod-mmchub-v1.ir-e1.cloudhub.io/erpconsole/
		]

	Args:
		environment		(Environment): [The environment for making requests.].
		token 			(str): [The Integrator fixed token.].
		debug 		 	(bool, optional): [Parameter to set the display of DEBUG logs.]. Defaults to False.

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

		self.headers = {}
		self.headers['Content-Type'] = 'application/json'
		self.headers['Authorization'] = f'Basic {self.token}'

	@AttemptRequests(success_codes=[200])
	def post_auth(self, integrator_token: str, client_token: str):
		auth = UnileverSiteMercadoAuth(integratorToken=integrator_token, clientToken=client_token)
		return requests.post(f'{self.environment.value}/auth', headers=self.headers, data=json.dumps(auth))

	@AttemptRequests(success_codes=[200])
	def post_product(self, products:UnileverSiteMercadoProductList):
		return requests.post(f'{self.environment.value}/products', headers=self.headers, data=unpack_payload_dict(products,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def post_product_stock(self, product_stock:UnileverSiteMercadoProductStockList):
		return requests.post(f'{self.environment.value}/productstock', headers=self.headers, data=unpack_payload_dict(product_stock,remove_null=True))

	@AttemptRequests(success_codes=[200])
	def post_product_price(self, product_price:UnileverSiteMercadoProductPriceList):
		return requests.post(f'{self.environment.value}/productprice', headers=self.headers, data=unpack_payload_dict(product_price,remove_null=True))
