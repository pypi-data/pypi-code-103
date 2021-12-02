# pylint:skip-file
"""
Wrapper for the functionality for various installation and project setup commands
see:
    `python setup.py help`
for more details
"""
from setuptools import setup, find_packages
from glob import glob
import os

PACKAGE_NAME = "autoreduce_frontend"

data_locations = [f"{PACKAGE_NAME}/templates/", f"{PACKAGE_NAME}/static/", f"{PACKAGE_NAME}/**/templates"]

data_files = []

for loc in data_locations:
    data_files.extend([f.split(f"{PACKAGE_NAME}/")[1] for f in glob(f"{loc}/**", recursive=True) if os.path.isfile(f)])
print(data_files)

setup(
    name=PACKAGE_NAME,
    version="22.0.0.dev8",  # when updating the version here make sure to also update webapp.D
    description="The frontend of the ISIS Autoreduction service",
    author="ISIS Autoreduction Team",
    url="https://github.com/autoreduction/autoreduce-frontend/",
    install_requires=[
        "autoreduce_qp>=22.0.0.dev17",
        "Django==3.2.8",
        "django_extensions==3.1.3",
        "django-user-agents==0.4.0",
        "djangorestframework==3.12.4",
        "django-filter==21.1",
        "django-crispy-forms==1.13.0",
        "django-tables2==2.4.1",
        "requests==2.25.1",
    ],
    packages=find_packages(),
    package_data={"": data_files},
    entry_points={"console_scripts": ["autoreduce-webapp-manage = autoreduce_frontend.manage:main"]})
