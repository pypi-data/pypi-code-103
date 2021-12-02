class State(object):
    def __init__(self, name: str, **state):
        self.state = {**state, 'name': name}

    def update(self, **kwargs) -> None:
        # In Python 3.9.0 or greater (released 17 October 2020):
        # self.state = self.state | kwargs
        self.state = {**self.state, **kwargs}

    def __repr__(self):
        return self.state['name']
