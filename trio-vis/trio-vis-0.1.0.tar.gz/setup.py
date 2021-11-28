# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['trio_vis']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.2.0,<22.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'rich>=9.13.0,<10.0.0',
 'trio-typing>=0.5.0,<0.6.0',
 'trio>=0.19.0,<0.20.0',
 'typing-extensions>=3,<4']

setup_kwargs = {
    'name': 'trio-vis',
    'version': '0.1.0',
    'description': 'Structured Concurrency visualizer for trio',
    'long_description': "# trio-vis\n\n`trio-vis` is a plugin for visualizing the scope history of your Trio project.\n\n![showcase](res/showcase.png)\n\n## How to use\n\n[sc-vis]: https://ianchen-tw.github.io/sc-vis\n[trio-vis-pip]: https://pypi.org/project/trio-vis/\n\n1. Install `trio-vis` via `pip install trio-vis` ([trio-vis-pip])\n2. In your source code, register `SC_Monitor()` as an Instrument while running `trio`\n\n    ```python\n    from trio_vis import SC_Monitor\n    trio.run(my_main_funciton, instruments=[SC_Monitor()])\n    ```\n\n3. After your program finished(or exited), the scope history would be stored in `./sc-logs.json`\n4. Upload your log file to [sc-visualizer][sc-vis], this is a twin project which focuses on visualization work.\n5. See your visualization result and help us improve.\n\n## Configuration\n\nImport `VisConfig` from `trio_vis`, and provide it as an argument while making your `SC_Monitor` object.\n\n```python\nfrom trio_vis import SC_Monitor, VisConfig\ncfg = VisConfig(print_task_tree=True)\ntrio.run(my_main_funciton, instruments=[SC_Monitor(config=cfg)])\n```\n\n## What does it do\n\n[ins-api]: https://trio.readthedocs.io/en/stable/reference-lowlevel.html#instrument-api\n\n`trio-vis` utilize the [Instrument API][ins-api] to monitor the lifetime of scopes (`Task`,`Nursery`).\nSince the [Instrument API][ins-api] doesn't provide callbacks for `Nursery`, we make inferences on our own.\n\n## Why visualize\n\n[trio]: https://github.com/python-trio/trio\n[trio-issue-413]: https://github.com/python-trio/trio/issues/413\n\n[curio]: https://github.com/dabeaz/curio\n[curio-monitor]: https://github.com/dabeaz/curio/blob/master/curio/monitor.py\n\nDerived from [curio], [trio] combines the idea of Structured Concurrency with existing single-threaded event-driven architecture. Which does make concurrent programs more manageable.\n\nTo make trio comparable with curio, contributors of trio also want to mimic the feature of [curio-monitor] to monitor the current system running state. This idea could be traced back to [trio-issue-413].\n\nSince then, projects have been developed (shown below).\n\nHowever, **trio is not curio**, at least lifetimes of scopes are structured by nature. I argue that by utilizing the feature of Structured Concurrency, we could visualize programs better.\nDevelopers could easily conceptualize their program, and bring their developing experience to the next level.\n\n### Previous work\n\n+ [python-trio/trio-monitor]: officail project developed under trio, however it use the old InstruementAPI\n+ [syncrypt/trio-inspector]: is a webmonitor to visualize the current state of the program\n+ [Tronic/trio-web-monitor]: a experiment to unified all previous work, developed by [Tronic](https://github.com/Tronic)\n+ [oremanj/trio-monitor]\n\n[python-trio/trio-monitor]:https://github.com/python-trio/trio-monitor\n[Tronic/trio-web-monitor]:https://github.com/Tronic/trio-web-monitor\n[syncrypt/trio-inspector]:https://github.com/syncrypt/trio-inspector\n[oremanj/trio-monitor]:https://github.com/oremanj/trio-monitor\n\n## Future plan\n\nThis project is in an early developing stage. Stay tuned for future update.\n",
    'author': 'Ian Chen',
    'author_email': 'ianre657@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ianchen-tw/trio-vis',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
