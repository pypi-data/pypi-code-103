from .base import ObjectListModel, BaseModel

class ClientDetail(BaseModel):

    def __init__(self,
        so=None,
        plant=None
    ):

        self.so = so
        self.plant = plant

class Request(BaseModel):

    def __init__(self,
        serviceheader=None
    ):

        self.serviceheader = serviceheader if serviceheader else ServiceHeader()

class ServiceHeader(BaseModel):

    def __init__(self,
        messagetime=None,
        messagereference=None,
        webstoreplatform=None,
        webstoreplatformversion=None,
        shippingsystemplatform=None,
        shippingsystemplatformversion=None,
        plugin=None,
        pluginversion=None
    ):

        self.messagetime = messagetime
        self.messagereference = messagereference
        self.webstoreplatform = webstoreplatform
        self.webstoreplatformversion = webstoreplatformversion
        self.shippingsystemplatform = shippingsystemplatform
        self.shippingsystemplatformversion = shippingsystemplatformversion
        self.plugin = plugin
        self.pluginversion = pluginversion

class Billing(BaseModel):

    def __init__(self,
        shipperAccountNumber=None,
        shippingPaymentType=None,
        billingAccountNumber=None,
    ):

        self.shipperAccountNumber = shipperAccountNumber
        self.shippingPaymentType = shippingPaymentType
        self.billingAccountNumber = billingAccountNumber
    
class DocumentImages(ObjectListModel):
    def __init__(self):
        super(DocumentImages, self).__init__(list=[], listObject=DocumentImage)

class DocumentImage(BaseModel):

    def __init__(self,
        documentImageType=None,
        documentImage=None,
        documentImageFormat=None
    ):

        self.documentImageType = documentImageType
        self.documentImage = documentImage
        self.documentImageFormat = documentImageFormat

class CustomerLogo(BaseModel):

    def __init__(self,
        logoImage=None,
        logoImageFormat=None
    ):

        self.logoImage = logoImage
        self.logoImageFormat = logoImageFormat

class CustomerBarcode(BaseModel):

    def __init__(self,
        barcodeType=None,
        barcodeContent=None,
        textBelowBarcode=None
    ):

        self.barcodeType = barcodeType
        self.barcodeContent = barcodeContent
        self.textBelowBarcode = textBelowBarcode

class Address(BaseModel):

    def __init__(self,
        streetLines=None,
        streetLines2=None,
        streetLines3=None,
        streetName=None,
        streetNumber=None,
        city=None,
        cityDistrict=None,
        stateOrProvinceCode=None,
        postalCode=None,
        countryCode=None
    ):

        self.streetLines = streetLines
        self.streetLines2 = streetLines2
        self.streetLines3 = streetLines3
        self.streetName = streetName
        self.streetNumber = streetNumber
        self.city = city
        self.cityDistrict = cityDistrict
        self.stateOrProvinceCode = stateOrProvinceCode
        self.postalCode = postalCode
        self.countryCode = countryCode


class Weight(BaseModel):

    def __init__(self,
        value=None
    ):

        self.value = value

class Dimensions(BaseModel):

    def __init__(self,
        length=None,
        width=None,
        height=None
    ):

        self.length = length
        self.width = width
        self.height = height

class Notification(ObjectListModel):

    def __init__(self):

        super(Notification, self).__init__(list=[], listObject=NotificationItem)
    

class NotificationItem(BaseModel):
    def __init__(self,
        code=None,
        message=None
    ):

        self.code = code
        self.message = message
