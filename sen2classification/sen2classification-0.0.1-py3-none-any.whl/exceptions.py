class LandCoverNotSeparatedError(Exception):
    '''Error raised when k-means classification wasn't successful. It is meant to be caught.
    '''
    pass


class MessageError(Exception):
    '''Error that stops code execution and prints error message.

    Attributes
    ----------

    feature : str
        feature that is missing or is invalid  
    value: str
        feature value
    message : str
        error message
    '''
    def __init__(self, feature : str, value : str, message : str):
        self.feature = feature
        self.value = value
        self.message = message

    def __str__(self):
        return f'{self.feature} = {self.value}. {self.message}'

class InvalidProductError(MessageError):
    def __init__(self, feature: str, value: str, message: str):
        super().__init__(feature, value, message)
    

class InvalidProductTypeError(MessageError):
    def __init__(self, feature: str, value: str, message: str):
        super().__init__(feature, value, message)
    

class InvalidNoDataValueError(MessageError):
    def __init__(self, feature: str, value: str, message: str):
        super().__init__(feature, value, message)
    

class MissingNecessaryBandError(MessageError):
    def __init__(self, feature: str, value: str, message: str):
        super().__init__(feature, value, message)


class BandNotResampledError(MessageError):
    def __init__(self, feature: str, value: str, message: str):
        super().__init__(feature, value, message)
        

class SetupNotCompletedError(MessageError):
    def __init__(self, feature: str, value: str, message: str):
        super().__init__(feature, value, message)
