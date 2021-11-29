from vinca.lib.terminal import AlternateScreen
from vinca.lib.readkey import readkey

def review(card):

	with AlternateScreen():

		lines = (card.path / 'lines').read_text().splitlines()
		print(lines.pop(0))  # print the first line
		for line in lines:
			readkey() # press any key to continue
			# TODO abort
			print(line)
		print('\n(end)')

		# grade the card
		char = readkey()
	
	return char

def make_string(card):
	return (card.path / 'lines').read_text().replace('\n',' / ')
