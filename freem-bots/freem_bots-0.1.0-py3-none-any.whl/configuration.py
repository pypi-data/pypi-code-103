import os


class Config:
	def __init__(self) -> None:
		self.discord_token = self._get_string('DISCORD_TOKEN')
		self.azure_token = self._get_string('AZURE_TOKEN', can_be_none = True)
		self.azure_location = self._get_string('AZURE_LOCATION', can_be_none = True)
		self.log_channel_id = self._get_integer('LOG_CHANNEL_ID', default_value = None, can_be_none = True)
		self.gcloud_voice_key = self._get_string('GCLOUD_VOICE_KEY', can_be_none = True)

	def _get_string(self, name: str, default_value: str = None, can_be_none: bool = False) -> str:
		missing = False
		env_value = os.getenv(name)
		if env_value is None or len(env_value) == 0:
			if default_value is None:
				missing = True
			else:
				return default_value
		else:
			return env_value
		if (missing or env_value is None) and not can_be_none:
			raise Exception(f"Missing environment variable '{name}'")
		else:
			return None

	def _get_integer(self, name: str, default_value: str = None, can_be_none: bool = False) -> int:
		str_value = self._get_string(name, default_value, can_be_none)
		try:
			return int(str_value)
		except:
			raise Exception(f"Cannot cast environment variable '{name}' into an integer")

	def _get_bool(self, name: str, default_value: bool = None, can_be_none: bool = False) -> bool:
		str_value = self._get_string(name, str(default_value), can_be_none).lower().strip()
		return str_value == '1' or str_value == 'true'
