# build-in imports
import 	sys
from 	dataclasses 	import dataclass
from 	typing 			import List

# external imports
import 	requests
from 	loguru 			import logger

# project imports
from napplib.utils.attempts_requests		import AttemptRequests
from napplib.utils.unpack_payload_dict		import unpack_payload_dict

@logger.catch()
@dataclass
class OminkONStoresController:
	token           : str
	tenant          : str
	application_id  : str

	def __post_init__(self):
		self.url = 'https://api-marketplace.onstores.com.br/HUB/v1'
		if not isinstance(self.token, str):
			raise TypeError(f'Please enter a valid Token. token: {self.token}')
		if not isinstance(self.application_id, str):
			raise TypeError(f'Please enter a valid Application ID. Application ID: {self.application_id}')
		if not isinstance(self.tenant, str):
			raise TypeError(f'Please enter a valid Tenant. Tenant: {self.tenant}')
		self.headers = {
			'token': f'{self.token}',
			'application_id': f'{self.application_id}',
			'tenant': f'{self.tenant}'
		}
	
	@AttemptRequests(success_codes=[200])
	def post_product(self, product):
		return requests.post(f'{self.url}/products', headers=self.headers, data=unpack_payload_dict(product))
	
	@AttemptRequests(success_codes=[200])
	def post_sku(self, sku, product_code):
		return requests.post(f'{self.url}/products/{product_code}/sku', headers=self.headers, data=unpack_payload_dict(sku))

	@AttemptRequests(success_codes=[200])
	def put_price(self, sku, price):
		return requests.put(f'{self.url}/products/skus/{sku}/price', headers=self.headers, data=unpack_payload_dict(price))

	@AttemptRequests(success_codes=[200])
	def put_stock(self, sku, stock):
		return requests.put(f'{self.url}/products/skus/{sku}/inventory', headers=self.headers, data=unpack_payload_dict(stock))
	
