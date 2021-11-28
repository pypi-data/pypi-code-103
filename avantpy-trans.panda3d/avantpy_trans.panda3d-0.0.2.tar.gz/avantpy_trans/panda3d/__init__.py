import os
import yaml

for path in os.listdir(os.path.dirname(__file__)):
    if path.endswith('.yaml'):
        dialect = path[:-5]
        with open(os.path.join(
                os.path.dirname(__file__),
                path
                ), 'r') as f:
            globals()[dialect] = yaml.safe_load(f)
