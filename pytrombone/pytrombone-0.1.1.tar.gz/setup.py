# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytrombone']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'pytrombone',
    'version': '0.1.1',
    'description': 'Wrapper for the Trombone project',
    'long_description': '# pytrombone\nPython wrapper for the Trombone project\n\n\nhttps://github.com/voyanttools/trombone\n\n## Installation\n```\n$ pip install pytrombone\n```\n\n## Usage\n### Examples\nLet takes a situation where we have a bunch of pdfs in a directory named \'./data/\',\nand we want to calculate the SMOG index on those PDFs.\n\n#### Making sure that Trombone works\n```python\nfrom pytrombone import Trombone, Cache, filepaths_loader\n\n# This will download the Trombone jar in the /tmp/ directory of your machine. \n# Note that Trombone is likely to be deleted on reboot, and will need to be downloaded again.\ntrombone = Trombone()\n\n# To get the version\nversion = trombone.get_version()\nprint(version)\n```\n\n#### Calculates the SMOG index of 2 files\n```python\n# To run Trombone on a single file use the run method.\n# Note that Trombone parameters are given in the form of a list of tuple of 2 elements.\n# The first element of the tuple is the parameter, and the second is its value.\n# Also note that Trombone will handle those 2 files concurrently \n# (it will be more performant to give many files at the same time rather than loop on each).\noutput, error = trombone.run([\n    (\'tool\', \'corpus.DocumentSMOGIndex\'),  # Choose the tool you want to use\n    (\'file\', \'./data/example1.pdf\'),\n    (\'file\', \'./data/example2.pdf\'),\n    (\'storage\', \'file\'),  # Optional, it allows Trombone to cache pre-processed files (use if you will use the file for many tools)\n])\noutput  # is the successful output of Trombone, in the form of a string\nerror  # is the failed output of Trombone, in the form of a string\n\n# You can serialize the output, which has the JSON format :\noutput = trombone.serialize_output(output)\n# output is now your results in the form of a dictionary\n```\n\n#### Calculates the SMOG index in batches\n\n```python\n# We first need to setup the cache file (it will allow you to re-run\n# your code in case of a problem without having to restart from the beginning)\ncache = Cache(\'./cache.db\')\n\n# Then, load the filepaths in batch. pytrombone has a function to do that.\n# Note that every file marked as processed will be ignored.\n# Also note that the Cache uses the filename of the file as reference.\nfor filepaths in filepaths_loader(\'./data/*.pdf\', 100, cache):\n    # Making tuples to fit the specification of Trombone parameters\n    files = [(\'file\', filepath) for filepath in filepaths]\n\n    output, error = trombone.run([\n        (\'tool\', \'corpus.DocumentSMOGIndex\'),  # Choose the tool you want to use\n        (\'storage\', \'file\'),  # Optional, it allows Trombone to cache pre-processed files (use if you will use the file for many tools)\n    ] + files)\n\n    try:\n        # If the serialization failed, it is because Trombone failed to performs the analysis.\n        # the failed files will be marked as failed in the cache and re-run on the next run.\n        # You may want to inspect the "error" variable for more information.\n        output = trombone.serialize_output(output)\n    except json.JSONDecoder:\n        filenames = [os.path.basename(filepath) for filepath in filepaths]\n        cache.mark_as_failed(filenames)\n        continue\n\n    output  # now has your results in the for of a dictionary\n```\n',
    'author': 'Gabriel Couture',
    'author_email': 'gacou54@ulaval.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
