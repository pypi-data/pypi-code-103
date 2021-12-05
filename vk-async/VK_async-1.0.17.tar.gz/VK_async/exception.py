
class ApiError(Exception):
    def __init__(self, method, error):
        super(Exception, self).__init__()
        self.method = method
        self.code = error['error_code']
        self.error = error



    def __str__(self):
        return '[{}] {}'.format(self.error['error_code'],
                                self.error['error_msg'])
