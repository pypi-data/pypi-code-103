
# Exception handling
class Error(Exception):
    """Base class for other exceptions"""
    pass

class ColumnReadingError(Error):
    """Raised when number of columns appears to be incorrect"""
    pass

class RowReadingError(Error):
    """Raised when number of rows appears to be incorrect"""
    pass

class RowAdjustError(Error):
    """Raised when some rows appear to be incorrectly grouped together"""
    pass
