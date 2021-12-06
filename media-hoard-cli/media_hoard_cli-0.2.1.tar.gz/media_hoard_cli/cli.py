"""Console script for Media Hoard CLI."""

import subprocess
import sys
import tempfile
from pathlib import Path

import click

from media_hoard_cli import hoard


@click.group()
def main():
    """Empty click anchor function."""


@click.command()
@click.option('--cfg-file',
              default="~/.config/media_hoard/config.yaml",
              help="path to config file")
@click.option('--part-file', default=None, help="path to parts file")
@click.option('--upload-dir', help="overide cfg upload-dir")
@click.argument('title')
@click.argument('src_file')
def add(cfg_file, part_file, upload_dir, title, src_file):
    """Add a new file from local host.

    TITLE: User friendly title
    SRC_FILE: path to item to add (path/to/file.pdf)
    """
    with tempfile.TemporaryDirectory() as dir_temp:
        item_id = hoard.get_id()
        dir_stage = dir_temp + '/' + item_id
        Path(dir_stage).mkdir()

        try:
            parts = hoard.parse_parts_file(part_file)

        except FileNotFoundError:
            parts = []

        try:
            cfg = hoard.parse_config_file(cfg_file, upload_dir)

            item = hoard.new_item(src_file, dir_stage, parts, title)

        except FileNotFoundError as exp:
            raise click.ClickException(exp)

        subprocess.run(['rsync', '-r', dir_stage, cfg['upload_dir']],
                       check=True)

        print(hoard.render_item(item, item_id, cfg['item_url']))

    return 0


main.add_command(add)

if __name__ == "__main__":
    sys.exit(main())  # pylint: disable=no-value-for-parameter
