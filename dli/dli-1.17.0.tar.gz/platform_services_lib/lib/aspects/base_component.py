from .component_aspect_wrapper import ComponentsAspectWrapper


class BaseComponent(metaclass=ComponentsAspectWrapper):

    def __init__(self, client=None):
        self.client = client