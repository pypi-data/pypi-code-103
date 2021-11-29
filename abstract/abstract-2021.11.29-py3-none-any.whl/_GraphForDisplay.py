from ._GraphWithoutDisplay import GraphWithoutDisplay, DEFAULT_PAD


class Graph(GraphWithoutDisplay):
	def get_svg(self, direction=None, pad=DEFAULT_PAD, **kwargs):
		"""
		:type direction: NoneType or str
		:type pad: NoneType or int or float
		:rtype: str
		"""
		return self.render(direction=direction or self._direction, pad=pad, **kwargs)._repr_svg_()

	def _repr_html_(self):
		return self.get_svg()

	def get_html(self, direction=None, pad=DEFAULT_PAD, **kwargs):
		from IPython.core.display import HTML
		return HTML(self.get_svg(direction=direction or self._direction, pad=pad, **kwargs))
