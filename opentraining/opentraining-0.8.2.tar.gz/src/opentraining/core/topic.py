from .node import Node


class Topic(Node):
    def __init__(self, title, path, docname, dependencies, userdata):
        super().__init__(
            title=title, 
            path=path, 
            docname=docname, 
            dependencies=dependencies, 
            userdata=userdata)
