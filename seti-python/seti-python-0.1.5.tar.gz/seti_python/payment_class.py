

from seti_python.class_tools import BasicResponse


class ResponseCreatePaymentData:
    id: str
    url: str

    def __init__(self, data: dict):
        try:
            self.id = data['id']
            self.url = data['url']
        except Exception:
            return


class ResponseCreatePayment(BasicResponse):
    data: ResponseCreatePaymentData

    def __init__(self, data: dict):
        self.msg = data['msg']
        self.res = data['res']
        if data['res'] == 200:
            self.data = ResponseCreatePaymentData(data['data'])
        else:
            self.data = ResponseCreatePaymentData({})
