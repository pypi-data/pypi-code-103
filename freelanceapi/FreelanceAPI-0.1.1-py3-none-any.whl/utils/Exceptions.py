class KeysDoNotMatchLength(Exception):
    """
    KeysDoNotMatch Length of Keys do not match with the dataset

    Args:
        Exception ([type]): Main Class for exceptions
    """

    def __init__(self, values: str, message: str = ""):
        self.values = values
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'Value:{self.values}  -> Msg:{self.message}'