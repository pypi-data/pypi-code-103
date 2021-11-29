from pdx import Config
from pdx import Log
import ntpath
import sys
import os


# Version of pdx-lib
VERSION = '0.0.1'

# Holds a Console, which tracks errors and warnings as it prints them
consoleInstance = None

# A holder for various types of data
data = {}

# Determine if running in debug mode
debug_mode = '--debug' in sys.argv or os.getenv('PDX_DEBUG')

# Determine if running in automated mode
auto_mode = '--autorun' in sys.argv

# Get name of script being run
script_name = ntpath.basename(sys.argv[0]).replace('.py', '') if ntpath.basename(sys.argv[0]) != "" else "command-line"

# Alias some commonly used config data (just for convenience)
username = Config.username
user_email = Config.user_email
user_home = Config.user_home
pdx_home = Config.pdx_home

# Hold log file info to make it available to scripts
logInstance = None  # This will be populated when logging starts


# ......................................
# Additional processing below this point
# (no additional variables declared below this point)
# ......................................


# Make sure the .pdx-lib directory exists
if not os.path.isdir(pdx_home):
    os.mkdir(pdx_home)
# Make sure the expected subdirectories exist as well
for dd in ['unit-test', 'preferences', 'config']:
    dp = os.path.join(pdx_home, dd)
    if not os.path.isdir(dp):
        os.mkdir(dp)

# If spaces exist in script name, use the last word (ex: "python -m test_all.py")
if ' ' in script_name:
    script_name = script_name.rsplit(None, 1)[-1]

# Start logging
if logInstance is None:
    logInstance = Log.Log(script_name, 'debug' if debug_mode else 'info', VERSION)
