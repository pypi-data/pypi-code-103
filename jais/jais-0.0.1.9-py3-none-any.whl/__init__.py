import os
from pathlib import Path

# Root for the JAIS package, not project.
# Root folder to load package default settings
ROOT_DIR = Path(__file__).parent
# Current Working Directory path to setup paths 
# for current project where JAIS package is installed.
JAIS_CWD = os.getenv('JAIS_CWD')
if JAIS_CWD is None:
    JAIS_CWD = ROOT_DIR

# Current package version
VERSION = '0.0.1.9'