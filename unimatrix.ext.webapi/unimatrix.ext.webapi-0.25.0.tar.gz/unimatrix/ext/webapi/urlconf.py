"""Declares functions to dynamically configure URLs."""
import logging

import fastapi
import ioc.loader
import marshmallow
import marshmallow.fields
import yaml


class URLRouteConfigurationSchema(marshmallow.Schema):
    kind = marshmallow.fields.String(
        required=True,
        validate=marshmallow.validate.OneOf(["endpoint"])
    )

    mount = marshmallow.fields.String(
        required=True,
        validate=marshmallow.validate.Regexp('^/.*$')
    )

    handler = marshmallow.fields.Method(
        required=True,
        deserialize='import_handler'
    )

    @property
    def logger(self):
        return self.context['logger']

    def import_handler(self, qualname: str):
        try:
            return ioc.loader.import_symbol(qualname)
        except ImportError:
            self.logger.error("Cannot import handler %s", qualname)
            return None


class URLConfigurationSchema(marshmallow.Schema):
    routes = marshmallow.fields.Nested(
        URLRouteConfigurationSchema,
        required=False,
        missing=list,
        many=True
    )



def fromfile(application: fastapi.FastAPI, fp: str) -> None:
    """Configures a :class:`~unimatrix.ext.webapi.Application` instance with
    the routes specified in the URL configuration file `fp`.
    """
    schema = URLConfigurationSchema(context={'logger': application.logger})
    urlconf = schema.load(yaml.safe_load(open(fp)) or {})

    for route in (urlconf.get('routes') or []):
        mount = route['mount']
        if route.get('kind') != "endpoint":
            raise NotImplementedError(route.get('kind'))
        if not route.get('handler'):
            application.logger.warning("Skipping mount %s", mount)
            continue
        route['handler'].add_to_router(application, route['mount'],)
