import subprocess

from polidoro_gitlab.gitlab import GitLab, Project, Pipeline

NAME = 'polidoro_gitlab'
VERSION = subprocess.run(['cat', 'VERSION'], capture_output=True).stdout.strip().decode()
