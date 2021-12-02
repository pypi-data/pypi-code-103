# Copyright 2017 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup

# Parse requirements file
with open('requirements.txt', 'r') as fh:
    _requires = fh.read().splitlines()


entry_points = {
    "console_scripts": [
        "pidb-db-init = pidb.__main__:db_init",
        "pidb-test-tasks = pidb.__main__:create_random_test_tasks",
        "pidb-test-taskgroup = pidb.__main__:create_random_test_taskgroup",
        "pidb-db-clean = pidb.__main__:db_clean",
        "pidb-db-reload = pidb.__main__:reload_data",
        "pidb-manager = pidb.__main__:flask_manager",
        #"pidb-run = pidb.__main__:run",
        #"pidb-run-gunicorn = pidb.__main__:run_gunicorn",
        "pidb-add-task = pidb.__main__:add_task",
        "pidb-add-template = pidb.__main__:add_template",
        "pidb-add-user = pidb.__main__:add_user",
        "pidb-config = pidb.__main__:config_from_file",
        "pidb-update-template = pidb.__main__:update_template",
        "pidb-db-bootstrap = pidb.__main__:bootstrap_db",
    ],
}


setup(
    name='pidb',
    version='6.0.1',
    author='H.C. Achterberg, M. Koek, A. Versteeg, T. Phil, M. Birhanu',
    author_email='h.achterberg@erasmusmc.nl, m.koek@erasmusmc.nl, a.versteeg@erasmusmc.nl, t.phil@erasmusmc.nl, m.birhanu@erasmusmc.nl',
    packages=['pidb',
              'pidb.api',
              'pidb.auth',
              'pidb.callbacks',
              'pidb.tests',
              'pidb.util',
             ],
    package_data={'pidb': ['templates/*', 'templates/**/*', 'static/*', 'static/**/*']},
    url='https://gitlab.com/radiology/population-imaging/population-imaging-database',
    project_urls={
        "Documentation": "https://population-imaging-database.readthedocs.io",
        "Code": "https://gitlab.com/radiology/population-imaging/population-imaging-database",
        "Issue tracker": "https://gitlab.com/radiology/population-imaging/population-imaging-database/issues",
    }, 
    license='LICENSE',
    description='Population Imaging Database (pidb) is a tool for collecting derived data in population imaging studies.',
    long_description=open('README.md').read(),
    python_requires="!=2.*,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Education',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: System :: Logging',
        'Topic :: Utilities',
    ],
    setup_requires=['wheel'],
    install_requires=_requires,
    entry_points=entry_points,
)
