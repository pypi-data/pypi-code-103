
from seti_python.class_tools import BasicResponse


class ResponseCreateWalletData:
    id: str
    url: str

    def __init__(self, data: dict):
        try:
            self.secret = data['secret']
        except Exception:
            return


class ResponseCreateWallet(BasicResponse):
    data: ResponseCreateWalletData

    def __init__(self, data: dict):
        self.msg = data['msg']
        self.res = data['res']
        if data['res'] == 200:
            self.data = ResponseCreateWalletData(data['data'])
        else:
            self.data = ResponseCreateWalletData()
