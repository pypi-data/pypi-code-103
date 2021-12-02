import json
import os
import pkgutil

try:
    config = json.loads(pkgutil.get_data("tests", "/conf/config.json"))
except:
    config = json.loads(pkgutil.get_data("tests", "/conf/config.example.json"))
