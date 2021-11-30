# This file contains paths to key directories
from pathlib import Path

# path to the GitHub repository
repo_dir = Path(__file__).resolve().parent.parent

# path to the Python package
pkg_dir = repo_dir / 'IPChecklists'

# directory where we keep data
data_dir = repo_dir / 'data'
