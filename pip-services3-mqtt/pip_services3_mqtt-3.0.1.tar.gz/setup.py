"""
Pip.Services MQTT
----------------------

Pip.Services is an open-source library of basic microservices.
The MQTT module contains a set of components for messaging using the Mqtt protocol. Contains the implementation of the components for working with messages: MqttMessageQueue, MqttConnectionResolver.
Links
`````

* `website <http://github.com/pip-services-python/>`_
* `development version <http://github.com/pip-services3-python/pip-services3-mqtt-python>`

"""

from setuptools import setup
from setuptools import find_packages

try:
    readme = open('readme.md').read()
except:
    readme = __doc__

setup(
    name='pip_services3_mqtt',
    version='3.0.1',
    url='http://github.com/pip-services3-python/pip-services3-mqtt-python',
    license='MIT',
    author='Conceptual Vision Consulting LLC',
    author_email='seroukhov@gmail.com',
    description='Communication components for Pip.Services in Python',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['config', 'data', 'test']),
    include_package_data=True,
    zip_safe=True,
    platforms='any',
    install_requires=[
        'pytest',
        'paho-mqtt',

        'pip-services3-messaging >= 3.1.1, < 4.0',
        'pip_services3_commons  >= 3.3.10, < 4.0',
        'pip_services3_components >= 3.5.4, < 4.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
