
class RatsError(Exception):
    """Error class to handle errors raised while parsing RATS files"""
    pass


class SamplesMissingError(Exception):
    """Error for when data samples are missing from a packet"""
    pass


class CouldNotConstructDataframeError(Exception):
    """Final error to handle failed dataframe creation"""
    pass


class DataframeNotValidError(Exception):
    """Dataframe fails to pass its validation check"""
    pass



