class InvalidQNameError(RuntimeError):
    
    def __init__(self, qname):
        message = "Invalid qname: " + qname
        super(InvalidQNameError, self).__init__(message)
