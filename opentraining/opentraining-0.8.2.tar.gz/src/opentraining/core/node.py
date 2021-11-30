from .element import Element, verify_is_path


class Node(Element):
    def __init__(self, title, path, docname, dependencies, userdata):
        for d in dependencies:
            verify_is_path(d, userdata=userdata)

        super().__init__(
            title=title, 
            path=path, 
            docname=docname, 
            userdata=userdata)
        self.dependencies = dependencies
