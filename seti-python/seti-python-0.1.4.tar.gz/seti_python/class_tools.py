class BasicResponse:
    msg: str
    res: int


class CompleteBasicaResponse(BasicResponse):

    def __init__(self, data: dict):
        self.msg = data['msg']
        self.res = data['res']
        if data['res'] == 200:
            self.data = ResponseCreateTransactionData(data['data'])
        else:
            self.data = ResponseCreateTransactionData({})


class ResponseCreateTransactionData:
    transaction_id: str

    def __init__(self, data: dict):
        try:
            self.transaction_id = data['transactionId']
        except Exception:
            return


class ResponseCreateTransaction(BasicResponse):
    data: ResponseCreateTransactionData

    def __init__(self, data: dict):
        self.msg = data['msg']
        self.res = data['res']
        if data['res'] == 200:
            self.data = ResponseCreateTransactionData(data['data'])
        else:
            self.data = ResponseCreateTransactionData({})


class ResponseCreateDispersionsData:
    ip: str
    reference: str
    timestamp: dict
    transactionType: str
    value: int

    def __init__(self, data: dict):
        try:
            self.ip = data['ip']
            self.reference = data["reference"]
            self.timestamp = data["timestamp"]
            self.transactionType = data["transactionType"]
            self.value = data["value"]
        except Exception:
            return


class ResponseCreateDispersions(BasicResponse):
    data: ResponseCreateDispersionsData

    def __init__(self, data: dict):
        self.msg = data['msg']
        self.res = data['res']
        if data['res'] == 200:
            self.data = ResponseCreateDispersionsData(data['data'])
        else:
            self.data = ResponseCreateDispersionsData({})
