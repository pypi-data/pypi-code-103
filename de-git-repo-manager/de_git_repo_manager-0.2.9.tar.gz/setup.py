# THIS FILE IS EXCLUSIVELY MAINTAINED by the project de V0.2.0 
""" setup of `de` namespace portions and root projects. """
import pprint
import sys

import setuptools

import de.setup_project
from de.setup_project import project_env_vars


de.setup_project.REPO_GROUP_SUFFIX = 'group'
pev = project_env_vars(from_setup=True)

if __name__ == "__main__":
    print("#  EXECUTING SETUPTOOLS SETUP: argv, kwargs  ###################")
    print(pprint.pformat(sys.argv, indent=3, width=75, compact=True))
    setup_kwargs = pev['setup_kwargs']
    print(pprint.pformat(setup_kwargs, indent=3, width=75, compact=True))
    setuptools.setup(**setup_kwargs)
    print("#  FINISHED SETUPTOOLS SETUP  ##################################")
