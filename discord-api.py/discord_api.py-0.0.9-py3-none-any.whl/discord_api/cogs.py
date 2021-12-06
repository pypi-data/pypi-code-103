from typing import Union

class Cogs:
    def __init__(self, name):
        self.name = name
        self.listens = {}

    def listen(self, name:str):
        def deco(coro):
            if name in self.listens:
                self.listens[name].append(coro)
            else:
                self.listens[name] = [coro]

    def setup(self):
        return self.listens