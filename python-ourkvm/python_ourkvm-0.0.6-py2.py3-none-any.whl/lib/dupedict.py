import json
from typing import Optional, Any, List, Tuple, Iterator

class DupeDict(dict[Any, Any]):
	"""
	DupeDict is a simple attempt at trying to support
	multiple identical keys in a dictionary, while remaining some speed.
	There's probably an academic word for this but I just call it DuplicateDict.
	"""
	internal_list :Optional[List[Tuple[Any, Any]]] = None

	def __setitem__(self, key :Any, value :Any) -> None:
		if self.internal_list is None:
			self.internal_list :List[Tuple[Any, Any]] = []

		index = len(self.internal_list)
		self.internal_list.append((key, value))
		if not self.get(key):
			dict.__setitem__(self, key, [index,])
		else:
			dict.__getitem__(self, key).append(index)

	def __getitem__(self, key :Any) -> Iterator[Any]:
		if self.internal_list:
			indexes = dict.__getitem__(self, key)
			for index in indexes:
				yield dict([self.internal_list[index]])

	def __iter__(self) -> Iterator[Any]:
		if self.internal_list:
			for key in dict.__iter__(self):
				for index in dict.__getitem__(self, key):
					yield self.internal_list[index]

	def __repr__(self) -> str:
		if self.internal_list:
			return str([dict([x]) for x in self.internal_list])
		else:
			return ''

	def json(self) -> List[Any]:
		return list(self)

class JsonEncoder:
	@staticmethod
	def _encode(obj :Any) -> Any:
		"""
		This JSON encoder function will try it's best to convert
		any archinstall data structures, instances or variables into
		something that's understandable by the json.parse()/json.loads() lib.
		_encode() will skip any dictionary key starting with an exclamation mark (!)
		"""
		if isinstance(obj, dict) and not hasattr(obj, 'json'):
			# We'll need to iterate not just the value that default() usually gets passed
			# But also iterate manually over each key: value pair in order to trap the keys.

			copy = {}
			for key, val in list(obj.items()):
				if isinstance(val, dict):
					# This, is a EXTREMELY ugly hack.. but it's the only quick way I can think of to trigger a encoding of sub-dictionaries.
					val = json.loads(json.dumps(val, cls=JSON))
				else:
					val = JsonEncoder._encode(val)

				if type(key) == str and key[0] == '!':
					pass
				else:
					copy[JsonEncoder._encode(key)] = val
			return copy
		elif hasattr(obj, 'json'):
			return obj.json()
		elif isinstance(obj, (list, set, tuple)):
			return [json.loads(json.dumps(item, cls=JSON)) for item in obj]
		else:
			return obj

class JSON(json.JSONEncoder, json.JSONDecoder):
	"""
	A safe JSON encoder that will omit private information in dicts (starting with !)
	"""
	def _encode(self, obj :Any) -> Any:
		return JsonEncoder._encode(obj)

	def encode(self, obj :Any) -> Any:
		return super(JSON, self).encode(self._encode(obj))


if __name__ == '__main__':
	base_hardware = DupeDict()
	base_hardware["cpu"] = "host"
	base_hardware["enable-kvm"] = True
	base_hardware["machine"] = "q35,accel=kvm"
	base_hardware["device"] = "intel-iommu"
	base_hardware["m"] = 8192
	base_hardware["device"] = "if=pflash,format=raw,readonly=on,file=/usr/share/ovmf/x64/OVMF_CODE.fd"
	base_hardware["device"] = "if=pflash,format=raw,readonly=on,file=/usr/share/ovmf/x64/OVMF_VARS.fd"

	print(json.dumps(base_hardware, cls=JSON))