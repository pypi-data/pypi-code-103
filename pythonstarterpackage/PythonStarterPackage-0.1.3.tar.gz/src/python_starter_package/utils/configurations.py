import os
import sys
import json

class Configurations:

	@classmethod
	def get_config(self):
		built_path = os.path.join(sys.prefix, 'config', 'config.json')
		dev_path = os.path.abspath(os.path.join(os.path.dirname(
			os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'config', 'config.json'))

		if os.path.exists(built_path):
			path = built_path
		else:
			path = dev_path

		with open(path, 'r') as f:
			return json.load(f)