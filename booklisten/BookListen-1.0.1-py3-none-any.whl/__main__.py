import click
from gtts import gTTS
from pathlib import Path

cli = click.Group()

BASE_PATH = Path.home() / "booklisten"
BASE_PATH.mkdir(exist_ok=True)

def convert_file(filename):
	click.secho(f'Opening {filename}', fg='green')
	with open(filename, 'r') as book:
		text = book.read().replace('\n', ' ')
		click.secho(f'Converting to audio...\nThis may take a while', fg='green')
		audio = gTTS(text)
		audio.save(f'{BASE_PATH / Path(filename).stem}.mp3')
		click.secho(f'Saved {Path(filename).stem}.mp3 to {BASE_PATH / Path(filename).stem}.mp3\n', fg='green')

@cli.command('convert')
@click.argument('filename')
def convert(filename):
    convert_file(filename)

@cli.command('convert-dir')
@click.argument('directory')
def convert_dir(directory):
	for file in Path(directory).glob('*.*'):
		convert_file(file)

if __name__ == '__main__':
    cli()
