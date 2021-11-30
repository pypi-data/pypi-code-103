from .base import APIEndpoint
from datetime import datetime

from mydhl.models.raterequests import *
from mydhl.constants.constants import *

class RateRequestMethods(APIEndpoint):

    def __init__(self, api):
        super(RateRequestMethods, self).__init__(api, "RateRequest")
    

    def get(self, 
        shipper, 
        recipient,
        packages,
        clientDetails=None,
        shipTimestamp=None,
        dropOffType=DropOffType.REGULAR_PICKUP, 
        unitOfMeasurement=Measurement.MEASUREMENT_METRIC, 
        content=ContentType.DOCUMENTS,
        paymentInfo=PaymentInfo.PAYMENT_DAP,
        nextBusinessDay='N'
    ):

        if not shipTimestamp: shipTimestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        data = {
            "RateRequest" : {
                'ClientDetails' : clientDetails,
                "RequestedShipment" : {
                    "DropOffType" : dropOffType,
                    "ShipTimestamp" : "{shipTimestamp} GMT+02:00".format(shipTimestamp=shipTimestamp),
                    "UnitOfMeasurement" : unitOfMeasurement,
                    "Content" : content,
                    "PaymentInfo" : paymentInfo,
                    "NextBusinessDay" : nextBusinessDay,
                    "Account" : self.api.account,
                    'Ship' : {
                        'Shipper' : shipper.getJSON(),
                        'Recipient' : recipient.getJSON()
                    },
                    'Packages' : packages.getJSON()
                }
            }
        }

        url = self.endpoint

        status, headers, respJson = self.api.post(url, data)
        return RateResponse().parse(respJson['RateResponse'])