import click
from gtts import gTTS
import os
from pathlib import Path

cli = click.Group()

if not os.path.exists(os.path.join(os.path.expanduser("~"), 'booklisten')):
    os.mkdir(os.path.join(os.path.expanduser("~"), 'booklisten'))


@cli.command('convert')
@click.argument('filename')
def convert(filename):
    click.secho(f'Opening {filename}', fg='green')
    with open(filename, 'r') as book:
        text = book.read().replace('\n', ' ')
        print(text)
        click.secho(f'Converting to audio...\nThis may take a while',
                    fg='green')
        audio = gTTS(text)
    audio.save(
        f'{os.path.join(os.path.expanduser("~"), "booklisten", Path(filename).stem)}.mp3'
    )


if __name__ == '__main__':
    cli()
