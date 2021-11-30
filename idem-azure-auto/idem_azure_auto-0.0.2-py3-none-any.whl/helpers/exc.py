class DescribeError(Exception):
    """Exception raised for resources not found in Azure."""

    def __init__(self, message: str):
        """
        Initialize an instance of this class.
        :param message: String message to present when rendering the exception.
        """
        self.message = message
        super().__init__(self.message)
