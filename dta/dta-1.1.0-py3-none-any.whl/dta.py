import sys

if sys.version_info[0] >= 3: # Python 3 or higher
	class ConvertedDict(object):
		def __init__(self, data):
			for name, value in data.items():
				setattr(self, name, self._wrap(value))

		def _wrap(self, value):
			if isinstance(value, (tuple, list, set, frozenset)): 
				return type(value)([self._wrap(v) for v in value])
			else:
				return ConvertedDict(value) if isinstance(value, dict) else value
	
	def Dict2Attr(data : object = None):
		for name, value in data.items():
			if " " in name:
				raise ValueError("Attribute name cannot contain space: {}".format(name))
		if isinstance(data, dict):
			return ConvertedDict(data)
		else:
			raise TypeError("Expected dict, got {}".format(type(data)))
else: # Python 2
	class ConvertedDict(object):
		def __init__(self, data):
			for name, value in data.iteritems():
				setattr(self, name, self._wrap(value))

		def _wrap(self, value):
			if isinstance(value, (tuple, list, set, frozenset)): 
				return type(value)([self._wrap(v) for v in value])
			else:
				return ConvertedDict(value) if isinstance(value, dict) else value
	def Dict2Attr(data : dict = None):
		for name, value in data.iteritems():
			if " " in name:
				raise ValueError("Attribute name cannot contain space: {}".format(name))
		return ConvertedDict(data)

def Attr2Dict(data : object = None):
	if isinstance(data, ConvertedDict):
		return data.__dict__
	else:
		raise TypeError("Expected ConvertedDict, got {}".format(type(data)))