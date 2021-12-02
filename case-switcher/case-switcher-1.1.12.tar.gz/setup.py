# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['__init__']
setup_kwargs = {
    'name': 'case-switcher',
    'version': '1.1.12',
    'description': 'Library to change the casing of strings.',
    'long_description': '<div align=center>\n<!-- Title: -->\n  <h1>Case Switcher</h1>\n<!-- Labels: -->\n  <!-- First row: -->\n  <img src="https://img.shields.io/badge/License-AGPL%20v3-blue.svg"\n   height="20"\n   alt="License: AGPL v3">\n  <img src="https://img.shields.io/badge/code%20style-black-000000.svg"\n   height="20"\n   alt="Code style: black">\n  <img src="https://img.shields.io/pypi/v/case-switcher.svg"\n   height="20"\n   alt="PyPI version">\n  <img src="https://img.shields.io/badge/coverage-100%25-success"\n   height="20"\n   alt="Code Coverage">\n  <h3>Change casing of a string.</h3>\n</div>\n\nThis library provides functions to change the casing convention of a\nstring.\n\nSupported cases:\n- camelCase\n- dot.case\n- kebab-case\n- PascalCase\n- snake_case\n- Title Case\n- UPPER.DOT.CASE\n- UPPER-KEBAB-CASE\n- UPPER_SNAKE_CASE\n\n### Install\n\n```shell\npip install case-switcher\n```\n\n### Demo\n\n```python\nimport caseswitcher\n\nsample = "avocado bagel-coffeeDONUTEclair_food.gravy"\n\ncaseswitcher.to_camel(sample)  # -> "avocadoBagelCoffeeDONUTEclairFoodGravy"\ncaseswitcher.to_dot(sample)  # -> "avocado.bagel.coffee.donut.eclair.food.gravy"\ncaseswitcher.to_kebab(sample)  # -> "avocado-bagel-coffee-donut-eclair-food-gravy"\ncaseswitcher.to_pascal(sample)  # -> "AvocadoBagelCoffeeDONUTEclairFoodGravy"\ncaseswitcher.to_snake(sample)  # -> "avocado_bagel_coffee_donut_eclair_food_gravy"\ncaseswitcher.to_title(sample)  # -> "Avocado Bagel Coffee DONUT Eclair Food Gravy"\ncaseswitcher.to_upper_dot(sample)  # -> "AVOCADO.BAGEL.COFFEE.DONUT.ECLAIR.FOOD.GRAVY"\ncaseswitcher.to_upper_kebab(sample)  # -> "AVOCADO-BAGEL-COFFEE-DONUT-ECLAIR-FOOD-GRAVY"\ncaseswitcher.to_upper_snake(sample)  # -> "AVOCADO_BAGEL_COFFEE_DONUT_ECLAIR_FOOD_GRAVY"\n```\n',
    'author': 'Matthew Burkard',
    'author_email': 'matthewjburkard@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/mburkard/case-switcher',
    'py_modules': modules,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
