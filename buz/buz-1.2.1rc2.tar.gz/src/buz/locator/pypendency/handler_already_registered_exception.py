class HandlerAlreadyRegisteredException(Exception):
    def __init__(self, handler_id: str):
        self.handler_id = handler_id
        super().__init__(f"Handler with id {handler_id} has been registered and cannot be registered another time")
