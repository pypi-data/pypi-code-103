import subprocess

from polidoro_cli.cli import CLI, CLI_DIR
from polidoro_cli.main import main

NAME = 'polidoro_cli'
VERSION = subprocess.run(['cat', 'VERSION'], capture_output=True).stdout.strip().decode()
