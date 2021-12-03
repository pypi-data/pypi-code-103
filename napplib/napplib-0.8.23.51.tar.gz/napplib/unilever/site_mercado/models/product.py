from dataclasses 	import dataclass
from typing 		import List


@dataclass
class UnileverSiteMercadoProduct:
	productTitle	: str
	ean				: str
	price			: str
	stockQty		: int
	sku				: str = None
	weight			: str = None


@dataclass
class UnileverSiteMercadoProductStock:
	sku			: str
	stockQty	: int


@dataclass
class UnileverSiteMercadoProductPrice:
	sku				: str
	price			: str
	originalPrice	: str = None

@dataclass
class UnileverSiteMercadoProductList:
	products : List[UnileverSiteMercadoProduct]

@dataclass
class UnileverSiteMercadoProductStockList:
	products : List[UnileverSiteMercadoProductStock]

@dataclass
class UnileverSiteMercadoProductPriceList:
	products : List[UnileverSiteMercadoProductPrice]
