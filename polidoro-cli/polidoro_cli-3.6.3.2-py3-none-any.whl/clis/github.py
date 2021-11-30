import re

from polidoro_argument import Command

from polidoro_cli import CLI


class GitHub(object):
    help = 'GitHub CLI commands'

    @staticmethod
    @Command(
        aliases=['cr'],
    )
    def create_release():
        for version in CLI.execute(
                'grep "VERSION =" * -rh --exclude-dir=venv', capture_output=True, show_cmd=False)[0].split('\n'):
            if version:
                search = re.search(r'VERSION = \'([\d\\.]*)\'', version)
                if search:
                    version = search.groups()[0]
                    CLI.execute(f'gh release create {version}')
