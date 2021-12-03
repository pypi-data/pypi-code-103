# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['ezstat']
setup_kwargs = {
    'name': 'ezstat',
    'version': '1.0',
    'description': 'OO For eazy statistics, inspired by `Statistics` class of the lib `deap` but more user-friendly',
    'long_description': "# Ezstat: Easy statistics\n\n\n\nOO For easy statistics, inspired by `Statistics` class of [deap](https://deap.readthedocs.io/en/master/index.html)\n\nIt is really easy and awesome! Believe me!\n\n![](logo.jpg)\n\n## Introduction\n\n`ezstat` is built for easy statistics, esp. for the history of iterations.\n\nThe main class `Statistics` just extends `dict{str:function}` (called statistics dict), function here will act on the object of statistics. The values of dict have not to be a function, if it is a string, then the object of method with the same name is applied.\n\nFrankly, It just borrows the idea from the `Statistics` class of [deap](https://deap.readthedocs.io/en/master/index.html). But unlike the author of deap, I just create it a subclass of dict, need not define strange methods.\n\nSee the following example and function `_call`, the underlying implementation.\n\n## Examples\n\nExample:\n\n```python\n>>> import numpy as np\n\n>>> T = np.random.random((100,100))\n>>> stat = Statistics({'mean': lambda x: np.mean(np.mean(x, axis=1)), 'max': lambda x: np.max(np.mean(x, axis=1)), 'shape':'shape'})\n>>> print(stat(T))\n>>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape': (100, 100)}\n\n>>> print(stat(T, split=True)) # split the tuple if it needs\n>>> {mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape-0': 100, 'shape-1': 100}\n```\n\n`MappingStatistics` is a subclass of `Statistics`. It just copes with iterable object, and maps the obect to an array by funcional attribute `key`.\n\nExample:\n\n```python\n>>> stat = MappingStatistics('mean', {'mean':np.mean, 'max':np.max})\n>>> print(stat(T))\n>>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957}\n```\n\nIn the exmaple, 'mean', an attribute of T, maps T to a 1D array.\n\n## Advanced Usage\n\n`Statistics` acts on a list/tuple of objects iteratively, gets a series of results,\nforming an object of `pandas.DataFrame`. In fact, it is insprited by `Statistics` class of third part lib [deap](https://deap.readthedocs.io/en/master/index.html). In some case, it collects a list of dicts of the statistics result for a series of objects. It is suggested to transform to DataFrame object.\n\n```python\nhistory = pd.DataFrame(columns=stat.keys())\nfor obj in objs:\n    history = history.append(stat(obj), ignore_index=True)\n```\n\n## To Do\n\n- [ ]  To define tuple of functions for the value of statistics dict.\n\n",
    'author': 'William Song',
    'author_email': '30965609+Freakwill@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Freakwill/ezstat',
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
