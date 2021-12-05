"""Declares :class:`RequestHandler`."""


class RequestHandler:

    def __init__(self, view_class, action):
        self.view_class = view_class
        self.action = action

    async def __call__(self, *args, **kwargs):
        view = self.view_class()
        view.view_class = self.view_class
        return await view.dispatch(*args, **kwargs)
