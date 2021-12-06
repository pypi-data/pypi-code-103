"""GH3 Python WSGI nano framework."""

__version__ = '1.0.0'

import json, typing, weakref

from werkzeug import (
    http     as wz_http,
    routing  as wz_routing,
    serving  as wz_serving,
    test     as wz_test,
    wrappers as wz_wrappers,
)

# Some aliases for easy importing
Rule     = wz_routing.Rule
RuleFactory = wz_routing.RuleFactory
Response = wz_wrappers.Response
Request  = wz_wrappers.Request

class Plugin:

  def add_plugins(self, app: 'Application'):
    """Override to add any other plugins."""

  def add_routes(self, app: 'Application'):
    """Override to add any routes."""

  def before_request(self, ctx: 'Context'):
    """Override to modify the context before a request has been dispatched."""

  def after_request(self, ctx: 'Context'):
    """Override to modify the context after a request has been dispatched."""


class Context:
  """The context of a single request/response

  Each request handler receives one and only one argument. This argument is the
  request context. The request context provides access to the request for
  reading request data, and also the response for providing data. Request
  handlers do not need to return anything. They just need to set some values on
  the response instance, such as the status code, the data, and the mime type in
  order to provide a response.

  This differs considerably from most web frameworks out there, in a pattern
  that Flask, for example, employs to *return* the response object from a
  request handler.
  """

  def __init__(self):

    #: The request instance.
    self.req: Request = None
    self.resp = None
    self.app = None
    self.urls = None
    self.environ = None
    self.route = None
    self.target = None
    self.endpoint = None
    self.endpoint_args = None

  def resp_type(self, mimetype):
    self.resp.mimetype = mimetype

  def resp_code(self, code):
    self.resp.status_code = code

  def resp_data(self, data):
    self.resp.set_data(data)

  def resp_charset(self, charset):
    self.resp.charset = charset

  def reply_data(self, data: str, mimetype, code=200):
    self.resp_code(code)
    self.resp_type(mimetype)
    self.resp_data(data)

  def reply_error(self, code):
    self.resp_code(code) # Set the code so we can get the status
    self.reply_data(self.resp.status, 'text/plain', code)

  def reply_text(self, text: str, code=200):
    self.reply_data(text, 'text/plain', code)

  def reply_html(self, html: str, code=200):
    self.reply_data(html, 'text/html', code)

  def reply_json(self, data: typing.Any, code=200):
    self.reply_data(json.dumps(data), 'application/json', code)


RequestTarget = typing.Callable[[Context], None]


class App:
  """The Application Context""" 

  #: The response type to create during a request.
  #: Change this to extend/modify the response type for every response.
  #:
  #: For example,
  #: ```python
  #: class Latin1Response(gh3.Response):
  #:   charset = 'latin-1'
  #:  
  #: app = gh3.App() 
  #: app.response_type = Latin1Response
  #: # all your latin are belong to us 
  #: ```
  #: Now the default charset for every response will be latin-1.
  response_type: typing.Type[Response] = Response

  #: The request type to create during a request.
  request_type = Request

  #: The rule type to create when making simple routes
  rule_type = Rule

  def __init__(self):
    #: Whether the app has been finalized, i.e. all routes and plugins are added.
    self.finalized: bool = False

    #: The bound route map.
    #: This is only available after finalize() has been called.
    self.route_map: wz_routing.MapAdapter = None

    #: List of routes that can be modified
    self.routes: list[wz_routing.RuleFactory] = []

    #: Map of endpoints to callable request handlers
    self.targets: dict[str, RequestTarget] = {}

    #: List of plugins which are loaded.
    self.plugins: typing.Iterable[Plugin] = []

  def finalize(self) -> bool:
    """Finalize the application context to make it ready to receive requests.

    Normally you will not need to call this, as it is autmatically called on
    receiving the first request. It can also be called multiple times safely.

    Once the app is finalized, you can no longer add routes or plugins.

    Returns:
      Whether the finalize happened or was skipped because finalize had already
      been called.
    """
    if self.finalized:
      return False
    self._plugins_add_plugins()
    self._plugins_add_routes()
    self.route_map = wz_routing.Map(self.routes)
    self.finalized = True
    return True

  def add_route(self, path: str, target: RequestTarget,
      endpoint: str = None, **rule_kw):
    """Add a named endpoint for a path to a target."""
    endpoint = endpoint or target.__name__
    rule = self.rule_type(path, endpoint=endpoint, **rule_kw)
    self.add_rule(rule)
    self.add_target(endpoint, target)

  def add_rule(self, rule: RuleFactory):
    self.routes.append(rule)

  def add_target(self, endpoint: str, target: RequestTarget):
    self.targets[endpoint] = target

  def add_plugin(self, plugin: Plugin):
    self.plugins.append(plugin)

  def request(self, environ) -> Context:
    ctx = Context()
    ctx.environ = environ
    ctx.app = self
    ctx.req = self.request_type(environ)
    ctx.resp = self.response_type()
    ctx.urls = self.route_map.bind_to_environ(environ)

    try:
      ctx.endpoint, ctx.endpoint_args = ctx.urls.match()
    except wz_routing.NotFound:
      ctx.reply_error(404)
      return ctx

    ctx.target = self.targets.get(ctx.endpoint)
    return ctx

  def dispatch(self, ctx: Context):
    if ctx.target:
      ctx.target(ctx)

  def __call__(self, environ, start_response):
    """WSGI callable function."""
    self.finalize()
    ctx = self.request(environ)
    self._plugins_before_request(ctx)
    self.dispatch(ctx)
    self._plugins_after_request(ctx)
    return ctx.resp(environ, start_response)

  def tester(self):
    return wz_test.Client(self)

  def debug(self, host='', port=8080, reload=True, debugger=True):
    wz_serving.run_simple(host, port, self,
        use_reloader=reload,
        use_debugger=debugger)

  def _plugins_add_plugins(self):
    for plugin in self.plugins:
      plugin.add_plugins(self)

  def _plugins_add_routes(self):
    for plugin in self.plugins:
      plugin.add_routes(self)

  def _plugins_before_request(self, ctx: Context):
    for plugin in self.plugins:
      plugin.before_request(ctx)

  def _plugins_after_request(self, ctx: Context):
    for plugin in self.plugins:
      plugin.after_request(ctx)


# vim: ft=python sw=2 ts=2 sts=2 tw=80
