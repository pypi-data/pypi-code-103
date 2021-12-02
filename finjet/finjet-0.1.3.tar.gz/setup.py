# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['finjet']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'finjet',
    'version': '0.1.3',
    'description': 'Dependency injection like FastAPI.',
    'long_description': "# finjet\n\n[![PyPI version](https://badge.fury.io/py/finjet.svg)](https://badge.fury.io/py/finjet)\n[![codecov](https://codecov.io/gh/elda27/finjet/branch/master/graph/badge.svg?token=Lnx3ZA0VKg)](https://codecov.io/gh/elda27/finjet)\n[![Codacy Badge](https://app.codacy.com/project/badge/Grade/0ccb2ee2bed64adb8c2e96a9b45aba95)](https://www.codacy.com/gh/elda27/finjet/dashboard?utm_source=github.com&utm_medium=referral&utm_content=elda27/finjet&utm_campaign=Badge_Grade)\n\nSimple dependency injection library like fastapi.\nIt can be used to turn your modules to loosely coupled parts. and configurations to allow you to easily re-use and test your code.\n\nDependency injection is performed on the arguments given with the `Depends` function as the default argument.\nThe inserted value will be given values of NamedTuple via `Container.configure` or the return value of the function.\n\n## Installation\n\nLatest PyPI stable release\n\n```bash\npip install finjet\n```\n\n## Example\n\n```python\nfrom typing import NamedTuple\nfrom finjet import Container, Depends, Singleton, inject\n\n\nclass Config(NamedTuple):\n    gear_ratio: int\n    tire_r: int = 100\n\n\nclass Engine:\n    # gear_ratio will be obtained from `Config`\n    def __init__(self, gear_ratio: int = Depends()) -> None:\n        self.gear_ratio = gear_ratio\n\n\nclass Tire:\n    count = 0\n\n    def __init__(self, tire_r: int = Depends()) -> None:\n        Tire.count += 1\n        # Actually tire_r is multiplied by instanced number of times.\n        self.tire_r = tire_r * Tire.count\n\n\ndef get_rotation_speed(engine: Engine = Depends(Engine)) -> int:\n    # Arguments of `Engine` class will inject from dependencies.\n    # In this example, the gear_ratio is configured 100 or 50\n    return engine.gear_ratio\n\n\n@inject\ndef get_tire_speed(\n    tire: Tire = Singleton(Tire),\n    rpm: int = Depends(get_rotation_speed)\n) -> float:\n    # Depends is always created such as factory pattern\n    # Singleton is only generate at once such as singleton pattern.\n    # The singleton object is shared in the Container class.\n    return tire.tire_r * rpm\n\n\ndef main():\n    container = Container()\n\n    # Configuration of container\n    container.configure(Config(100, 100))\n    with container:\n        print('Speed:', get_tire_speed())  # 10000\n        print('#Tire:', Tire.count)  # 1\n\n    # If the configuration value is changed, the displaying value is difference.\n    # But `Tire.count` is same so that a second argument, the Tire object is re-used.\n    container.configure(Config(20, 100))\n    with container:\n        print('Speed:', get_tire_speed())  # 2000\n        print('#Tire:', Tire.count)  # 1\n\n    # If the configuration value is changed, the displaying value is difference.\n    # The `Tire` object is updated.\n    container.configure(Config(20, 10))\n    with container:\n        print('Speed:', get_tire_speed())  # 400\n        print('#Tire:', Tire.count)  # 2\n\n\nif __name__ == '__main__':\n    main()\n\n```\n",
    'author': 'elda27',
    'author_email': 'kaz.birdstick@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
