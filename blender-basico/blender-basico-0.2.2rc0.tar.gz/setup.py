# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['blender_basico']

package_data = \
{'': ['*'],
 'blender_basico': ['static/blender_basico/fonts/*',
                    'static/blender_basico/images/*',
                    'static/blender_basico/scripts/tutti/*',
                    'static/blender_basico/scripts/vendor/*',
                    'static/blender_basico/styles/*',
                    'static/blender_basico/styles/bootstrap/*',
                    'static/blender_basico/styles/bootstrap/mixins/*',
                    'static/blender_basico/styles/bootstrap/utilities/*',
                    'static/blender_basico/styles/bootstrap/vendor/*',
                    'templates/blender_basico/_footer.html',
                    'templates/blender_basico/_footer.html',
                    'templates/blender_basico/_footer.html',
                    'templates/blender_basico/_navbar.html',
                    'templates/blender_basico/_navbar.html',
                    'templates/blender_basico/_navbar.html',
                    'templates/blender_basico/base.html',
                    'templates/blender_basico/base.html',
                    'templates/blender_basico/base.html']}

install_requires = \
['django-pipeline>=2,<3',
 'django>=2.1,<3.0',
 'jsmin>=3.0.0,<4.0.0',
 'libsasscompiler>=0.1.5,<0.2.0',
 'pypugjs>=5.9.8,<6.0.0']

entry_points = \
{'console_scripts': ['update-bwa = tools:update']}

setup_kwargs = {
    'name': 'blender-basico',
    'version': '0.2.2rc0',
    'description': 'Django shared app, featuring essential components for blender.org sites.',
    'long_description': None,
    'author': 'Francesco Siddi',
    'author_email': 'francesco@blender.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
