import sys
import doctest
from textblob import TextBlob
from googletrans import Translator, constants


def hello_guys(text):
	"""Returns a sympathetic greeting in the language of the given text

	Initializes a translator (form Google Translator API), then detects the given
	text language with TextBlob and finally returns a sympathetic greeting in
	the corresponding language

	Args:
		text (str): given text in a specific language (optional).

	Returns:
		str: the sympathetic greeting in the corresponding
		language.

	>>> hello_guys("saucisson")
	'Bonjour gars!'
	>>> hello_guys("donna")
	'Ciao ragazzi!'
	>>> hello_guys("pizza")
	'Hello guys!'
	>>> hello_guys("维尼熊")
	'大家好！'
	>>> hello_guys("ブラックホール")
	'こんにちはみんな！'
	>>> hello_guys("reich")
	'Hallo Leute!'
	>>> hello_guys("despacito")
	'¡Hola chicos!'
	>>> hello_guys(None)
	'No text but hello guys!'
	"""
	translator = Translator()

	if text:
		text_blob = TextBlob(text)
		lang = text_blob.detect_language()
		if lang != "en":
			translation = translator.translate("Hello guys!", src="en", dest=lang)
			sympathetic_greeting = translation.text
		else:
			sympathetic_greeting = "Hello guys!"
	else:
		sympathetic_greeting = "No text but hello guys!"

	return sympathetic_greeting


def main():
	"""Main function

	Gets the first command line argument then prints the return value of hello_guys
	function with the command line argument as parameter
	"""
	if len(sys.argv) > 1:
		result = hello_guys(sys.argv[1])
	else:
		result = hello_guys(None)

	print(result)

	doctest.testmod()

	#/usr/share/sphinx/scripts/python3/sphinx-quickstart
	#/usr/share/sphinx/scripts/python3/sphinx-apidoc -o ./source ../..


if __name__ == '__main__':
	main()