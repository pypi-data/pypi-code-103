from setuptools import setup

version = '0.0.4.7'

setup(
    name='django-routine',
    version=version,
    description='A Django app for managing routines.',
    author='Daniel Cuznetov',
    author_email='danielcuznetov04@gmail.com',
    packages=['django_routine'],
    entry_points={
        "console_scripts": [
            "startproject = django_routine.start:start",

        ]
    },
    install_requires=['djangorestframework', 'django', 'django-rest-swagger', 'drf_yasg'],
)
