from typing import List, Optional


class PayeerError(Exception):
    def __init__(self, errors: List[str]):
        self.errors = errors

    def __str__(self):
        return str(self.errors)


class PayeerValidationError(Exception):
    def __init__(self, msg: str, order_id: Optional[str] = None):
        self.msg = msg
        self.order_id = order_id

    def __str__(self):
        return str(self.msg)


class AlreadyPaid(Exception):
    def __init__(self, order_id: str):
        self.order_id = order_id
