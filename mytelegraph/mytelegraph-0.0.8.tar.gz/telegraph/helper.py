import re
import argparse

def tag_it(tag: str, string: str):
	if tag == "img":
		value = f"<img src='{string}'></img>"
		return value
	if tag == "br":
		value = "<br>"
		return value
	if tag == "a":
		link = re.findall(r'\[(.*?)\]', string)
		if link:
			link = link[0]
			string = string.split('[')[0]
			value = f"<{tag} href='{link}'>{string}</{tag}>"
			return value
	else:
		value = f"<{tag}>{string}</{tag}>"
		return value

def main(filename: str):
	data = []
	with open(filename) as f:
		file_to_list = f.read().splitlines()
		for file_text in file_to_list:
			tag = file_text.split(':')[0]
			string = file_text.replace(tag + ":" , '')
			string = tag_it(tag, string)

			data.append(string)
	data = "\n".join([v for v in data])
	f = open(filename + ".html", "w")
	f.write(data)
