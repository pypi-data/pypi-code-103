from .base import APIEndpoint

from inktool.models.orders import OrderList, OrderConfirmResponse

class OrderMethods(APIEndpoint):

    def __init__(self, api):
        super().__init__(api, 'orders')

    def getOpenOrders(self):

        url = 'getOrder'
        data = None

        status, headers, respJson = self.api.get(url, data)
        if status != 200: return OrderList().parseError(respJson)

        return OrderList().parse(respJson['orders'])
    
    def confirmOrders(self, idList):

        url = 'confirmOrder'
        data = { 'orderIdList' : idList }

        status, headers, respJson = self.api.post(url, data)
        if status != 200: return OrderConfirmResponse().parseError(respJson)

        return OrderConfirmResponse().parse(respJson)