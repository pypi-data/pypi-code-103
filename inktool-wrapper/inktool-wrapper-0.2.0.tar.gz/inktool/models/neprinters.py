from .base import BaseModel, ObjectListModel

class NEPrinterList(ObjectListModel):

    def __init__(self):
        super().__init__(list=[], listObject=NEPrinter)

class NEPrinter(BaseModel):
    
    def __init__(self,
        printerId=None,
        userId=None,
        name=None,
        brand=None
    ):
        super().__init__()

        self.printerId = printerId
        self.userId = userId
        self.name = name
        self.brand = brand

class NEPrinterConfirmResponse(BaseModel):

    def __init__(self,
        success=None,
        failed=None
    ):

        super().__init__()

        self.success = success
        self.failed = failed