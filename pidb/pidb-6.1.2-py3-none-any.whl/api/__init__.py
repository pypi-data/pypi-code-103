from flask_restx import Api


class RegisteredApi(Api):
    """ This class keeps track of all registered api's. """
    api_map = {}

    def __init__(self, app=None, version='1.0', *args, **kwargs):
        super().__init__(app, version, *args, **kwargs)
        if version in self.api_map:
            raise ValueError(f"Api with version {version} already registered.")
        self.api_map[version] = app
