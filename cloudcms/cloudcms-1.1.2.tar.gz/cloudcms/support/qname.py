from ..error import InvalidQNameError

class QName(object):
    
    def __init__(self, namespace, name):
        self.namespace = namespace
        self.name = name

    def __str__(self):
        return self.namespace + ':' + self.name

    @classmethod
    def create(cls, qname=None, namespace=None, name=None):
        result = None
        if qname is not None:
            x = qname.find(':')
            if x > -1:
                result = QName(qname[:x], qname[x+1:])
            else:
                raise InvalidQNameError(qname)
        elif namespace is not None and name is not None:
            result = QName(namespace, name)

        return result