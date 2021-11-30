from .node import Node
from . import errors


class Person(Node):  # is-a Node only because that holds path,
                     # docname, and userdata
    def __init__(self, title, path, docname, userdata, 
                 firstname, lastname):
        super().__init__(
            title=title, 
            path=path, 
            docname=docname, 
            userdata=userdata,
            dependencies=[], 
            )

        if not firstname:
            raise OpenTrainingError('firstname must be set')
        if not lastname:
            raise OpenTrainingError('lastname must be set')

        self.firstname = firstname
        self.lastname = lastname
