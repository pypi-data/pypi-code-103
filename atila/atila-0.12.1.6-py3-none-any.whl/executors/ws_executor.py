from . import wsgi_executor
from skitai.protocols.sock.impl.http import respcodes
from skitai.backbone.http_response import catch

class Executor (wsgi_executor.Executor):
	def __call__ (self):
		self.was = self.env ["skitai.was"]
		current_app, wsfunc = self.env.get ("websocket.handler")
		content = wsfunc (self.was, **self.env.get ("websocket.params", {}))
		return content
