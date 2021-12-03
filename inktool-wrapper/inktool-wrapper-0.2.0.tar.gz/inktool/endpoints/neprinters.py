from .base import APIEndpoint

from inktool.models.neprinters import NEPrinterList, NEPrinterConfirmResponse

class NEPrinterMethods(APIEndpoint):

    def __init__(self, api):
        super().__init__(api, 'orders')

    def getOpenNEPrinters(self):

        url = 'getNEPrinter'
        data = None

        status, headers, respJson = self.api.get(url, data)
        if status != 200: return NEPrinterList().parseError(respJson)

        return NEPrinterList().parse(respJson['printers'])
    
    def confirmNEPrinters(self, idList):

        url = 'confirmNEPrinter'
        data = { 'printerIdList' : idList }

        status, headers, respJson = self.api.post(url, data)
        if status != 200: return NEPrinterConfirmResponse().parseError(respJson)

        return NEPrinterConfirmResponse().parse(respJson)