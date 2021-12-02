import demoji


class Demoji:
	def remove_emojis(self, content: str, separator: str = ' ') -> str:
		return demoji.replace_with_desc(content, separator)
