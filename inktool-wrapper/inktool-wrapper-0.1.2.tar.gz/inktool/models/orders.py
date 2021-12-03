from .base import BaseModel, ObjectListModel

class OrderList(ObjectListModel):

    def __init__(self):
        super().__init__(list=[], listObject=Order)

class Order(BaseModel):
    
    def __init__(self,
        orderId=None,
        clientId=None,
        items=None,
        adres=None
    ):
        super().__init__()

        self.orderId = orderId
        self.clientId = clientId
        self.items = items if items else OrderItemList()
        self.adres = adres if adres else OrderAdres()


class OrderItemList(ObjectListModel):

    def __init__(self):
        super().__init__(list=[], listObject=OrderItem)

class OrderItem(BaseModel):

    def __init__(self,
        id=None,
        amount=None
    ):
        super().__init__()

        self.id = id
        self.amount = amount

class OrderAdres(BaseModel):

    def __init__(self,
        type=None,
        street=None,
        houseNumber=None,
        busNumber=None,
        postalCode=None,
        city=None,
        country=None,
        pickup=None
    ):

        super().__init__()

        self.type = type
        self.street = street
        self.houseNumber = houseNumber
        self.busNumber = busNumber
        self.postalCode = postalCode
        self.city = city
        self.country = country
        self.pickup = pickup

class OrderConfirmResponse(BaseModel):

    def __init__(self,
        success=None,
        failed=None
    ):

        super().__init__()

        self.success = success
        self.failed = failed