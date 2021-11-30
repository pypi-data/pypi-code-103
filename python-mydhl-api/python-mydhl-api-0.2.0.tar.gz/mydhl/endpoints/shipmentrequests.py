from .base import APIEndpoint
import datetime

from mydhl.models.shipmentrequests import *
from mydhl.constants.constants import *

class ShipmentRequestMethods(APIEndpoint):

    def __init__(self, api):
        super(ShipmentRequestMethods, self).__init__(api, "ShipmentRequest")
    
    def shipPackage(self,
        serviceType,
        shipper, 
        recipient,
        packages,
        internationalDetail,
        labelOptions=None,
        shipTimestamp=None,
        dropOffType=DropOffType.REGULAR_PICKUP, 
        unitOfMeasurement=Measurement.MEASUREMENT_METRIC,
        paymentInfo=PaymentInfo.PAYMENT_DAP,
        currency='EUR',
        invoicePDF=None,
    ):

        # Create timestamp from now +2 hours if timestamp is not given
        if not shipTimestamp: 
            shipTime = datetime.datetime.now() + datetime.timedelta(hours=2)
            shipTimestamp = shipTime.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Starting data
        data = {
            "ShipmentRequest": {
                "RequestedShipment": {
                    "ShipmentInfo": {
                        "LabelType": "PDF",
                        "DropOffType": dropOffType,
                        "ServiceType": serviceType,
                        "Account": self.api.account,
                        "Currency": currency,
                        "UnitOfMeasurement": unitOfMeasurement,
                    },
                    "ShipTimestamp": "{shipTimestamp} GMT+02:00".format(shipTimestamp=shipTimestamp),
                    "PaymentInfo": paymentInfo,
                    "InternationalDetail" : internationalDetail.getJSON(),
                    "Ship": {
                        "Shipper": shipper.getJSON(),
                        "Recipient": recipient.getJSON()
                    },
                    "Packages": packages.getJSON()
                }
            }
        }
        
        # If labelOptions is added, send it with the request
        if labelOptions: data['ShipmentRequest']['RequestedShipment']['ShipmentInfo']['LabelOptions'] = labelOptions.getJSON()
        
        # If PDF of invoice is added, send it with the request
        if invoicePDF:
            specialServices = SpecialServices()
            serv = SpecialService(serviceType="WY")
            specialServices.add(serv)
            
            # Enable paperless trade
            data['ShipmentRequest']['RequestedShipment']['ShipmentInfo']['PaperlessTradeEnabled'] = 'true'
            
            # Add WY service
            data['ShipmentRequest']['RequestedShipment']['ShipmentInfo']['SpecialServices'] = [{ 'Service' : [] }]
            data['ShipmentRequest']['RequestedShipment']['ShipmentInfo']['SpecialServices'][0]['Service'] = specialServices.getJSON()
            
            # Add image in B64
            data['ShipmentRequest']['RequestedShipment']['ShipmentInfo']['PaperlessTradeImage'] = invoicePDF
            data['ShipmentRequest']['RequestedShipment']['ShipmentInfo']['DocumentImages'] = [{ 'DocumentImage' : { 'DocumentImageType' : 'DCL', 'DocumentImage' : invoicePDF, 'DocumentImageFormat' : 'PDF'}}]


        print(data)

        # url = self.endpoint

        # status, headers, respJson = self.api.post(url, data)

        # print(respJson)
        # return ShipmentResponse().parse(respJson['ShipmentResponse'])