
from seti_python.class_tools import BasicResponse


# Read total CashOUts
class ValidateUsersExist:
    exist = False

    def __init__(self, data: dict):
        self.exist = data['exist']


class ResponseValidateUsersExist(BasicResponse):
    data: ValidateUsersExist

    def __init__(self, data: dict):
        self.msg = data['msg']
        self.res = data['res']
        if data['res'] == 200:
            self.data = ValidateUsersExist(data['data'])
        else:
            self.data = ValidateUsersExist({})

# Create user Data


class NewUsers:
    secret: str

    def __init__(self, data: dict):
        try:
            self.secret = data['secret']
        except Exception:
            self.secret = ""


class ResponseCreateUser(BasicResponse):
    data: NewUsers

    def __init__(self, data: dict):
        self.msg = data['msg']
        self.res = data['res']

        if data['res'] == 200:
            self.data = NewUsers(data['data'])
        else:
            self.data = NewUsers({})
