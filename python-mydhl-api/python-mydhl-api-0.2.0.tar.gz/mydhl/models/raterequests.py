from mydhl.models.shipmentrequests import Address
from .base import ObjectListModel, BaseModel
from .general import ClientDetail, Request, Address, Notification, NotificationItem
from mydhl.constants.constants import *

class RateResponse(BaseModel):

    def __init__(self, 
        provider=None
    ):

        self.provider = provider if provider else Provider()
    

class Provider(ObjectListModel):

    def __init__(self):

        super(Provider, self).__init__(list=[], listObject=ProviderItem)

    
class ProviderItem(BaseModel):

    def __init__(self,
        code=None,
        notification=None,
        service=None
    ):

        self.code = code
        self.notification = notification if notification else Notification()
        self.service = service if service else Service()

class Service(ObjectListModel):

    def __init__(self):

        super(Service, self).__init__(list=[], listObject=ServiceItem)
    
class ServiceItem(BaseModel):

    def __init__(self,
        type=None,
        totalNet=None,
        charges=None,
        deliveryTime=None,
        cutOffTime=None,
        nextBusinessDayInd=None
    ):

        self.type = type
        self.totalNet = totalNet if totalNet else TotalNet()
        self.charges = charges if charges else Charges()
        self.deliveryTime = deliveryTime
        self.cutOffTime = cutOffTime
        self.nextBusinessDayInd = nextBusinessDayInd
    
    def getTypeDisplay(self):

        if self.type:
            if self.type in PRODUCTS_GLOBAL: return PRODUCTS_GLOBAL[self.type]
    
        return 'TYPE_NOTFOUND'


class TotalNet(BaseModel):
    
    def __init__(self,
        currency=None,
        amount=None
    ):

        self.currency = currency
        self.amount = amount

class Charges(BaseModel):

    def __init__(self,
        currency=None,
        charge=None
    ):

        self.currency = currency
        self.charge = charge if charge else ChargeList()


class ChargeList(ObjectListModel):

    def __init__(self):

        super(ChargeList, self).__init__(list=[], listObject=Charge)


class Charge(BaseModel):

    def __init__(self,
        chargeCode=None,
        chargeType=None,
        chargeAmount=None
    ):

        self.chargeCode = chargeCode
        self.chargeType = chargeType
        self.chargeAmount = chargeAmount


class RateRequest(BaseModel):

    def __init__(self,
        clientDetail=None,
        request=None,
        requestedShipment=None
    ):

        self.clientDetail = clientDetail if clientDetail else ClientDetail()
        self.request = request if request else Request()
        self.requestedShipment = requestedShipment if requestedShipment else RequestedShipment()

class RequestedShipment(BaseModel):

    def __init__(self,
        dropOffType=None,
        shipTimestamp=None,
        unitOfMeasurement=None,
        content=None,
        paymentInfo=None,
        nextBusinessDay=None,
        account=None,
        ship=None,
        packages=None
    ):

        self.dropOffType = dropOffType
        self.shipTimestamp = shipTimestamp
        self.unitOfMeasurement = unitOfMeasurement
        self.content = content
        self.paymentInfo = paymentInfo
        self.nextBusinessDay = nextBusinessDay
        self.account = account
        self.ship = ship if ship else Ship()
        self.packages = packages if packages else Packages()

class Ship(BaseModel):

    def __init__(self,
        shipper=None,
        recipient=None
    ):

        self.shipper = shipper if shipper else Address()
        self.recipient = recipient if recipient else Address()

class Packages(BaseModel):

    def __init__(self,
        requestedPackages=None
    ):
        self.requestedPackages = requestedPackages if requestedPackages else RequestedPackages()

    def items(self):
        return self.requestedPackages.items()

    def remove(self, item):
        return self.requestedPackages.remove(item)
        
    def add(self, item):
        return self.requestedPackages.add(item)

class RequestedPackages(ObjectListModel):

    def __init__(self):
        super(RequestedPackages, self).__init__(list=[], listObject=RequestedPackage)
    

class RequestedPackage(BaseModel):

    def __init__(self,
        _number=None,
        weight=None,
        dimensions=None
    ):
        self._number = _number
        self.weight = weight if weight else Weight()
        self.dimensions = dimensions if dimensions else Dimensions()