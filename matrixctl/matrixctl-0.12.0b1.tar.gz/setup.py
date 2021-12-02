# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['matrixctl',
 'matrixctl.addons',
 'matrixctl.addons.adduser',
 'matrixctl.addons.adduser_jitsi',
 'matrixctl.addons.check',
 'matrixctl.addons.delete_local_media',
 'matrixctl.addons.delroom',
 'matrixctl.addons.deluser',
 'matrixctl.addons.deluser_jitsi',
 'matrixctl.addons.deploy',
 'matrixctl.addons.get_event',
 'matrixctl.addons.get_event_context',
 'matrixctl.addons.get_events',
 'matrixctl.addons.is_admin',
 'matrixctl.addons.joinroom',
 'matrixctl.addons.maintenance',
 'matrixctl.addons.make_room_admin',
 'matrixctl.addons.purge_history',
 'matrixctl.addons.purge_remote_media',
 'matrixctl.addons.report',
 'matrixctl.addons.reports',
 'matrixctl.addons.rooms',
 'matrixctl.addons.server_notice',
 'matrixctl.addons.set_admin',
 'matrixctl.addons.start',
 'matrixctl.addons.stop',
 'matrixctl.addons.update',
 'matrixctl.addons.upload',
 'matrixctl.addons.user',
 'matrixctl.addons.users',
 'matrixctl.addons.version',
 'matrixctl.handlers']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.20,<4.0.0',
 'Jinja2>=3.0.1,<4.0.0',
 'ansible-runner>=1.4.7,<3.0.0',
 'attrs>=21.2.0,<22.0.0',
 'coloredlogs>=15.0.1,<16.0.0',
 'httpx[http2]>=0.20,<0.22',
 'paramiko>=2.7.2,<3.0.0',
 'psycopg>=3.0.5,<4.0.0',
 'ruamel.yaml>=0.17.10,<0.18.0',
 'sshtunnel>=0.4.0,<0.5.0',
 'xdg>=5.1.0,<6.0.0']

extras_require = \
{'docs': ['sphinx>=3.5.1,<5.0.0',
          'sphinx-autodoc-typehints>=1.12.0,<2.0.0',
          'sphinxcontrib-programoutput>=0.16,<0.18',
          'numpydoc>=1.1.0,<2.0.0',
          'sphinx_rtd_theme>=1.0.0,<2.0.0']}

entry_points = \
{'console_scripts': ['matrixctl = matrixctl.__main__:main']}

setup_kwargs = {
    'name': 'matrixctl',
    'version': '0.12.0b1',
    'description': 'Control, manage, provision and deploy matrix homeservers.',
    'long_description': '![GitHub](https://img.shields.io/github/license/MichaelSasser/matrixctl?style=flat-square)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/matrixctl?style=flat-square)\n![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/michaelsasser/matrixctl?style=flat-square)\n![GitHub Release Date](https://img.shields.io/github/release-date/michaelsasser/matrixctl?style=flat-square)\n![Matrix](https://img.shields.io/matrix/matrixctl:matrix.org?server_fqdn=matrix.org&style=flat-square)\n\n# MatrixCtl\n\nMatrixCtl is a simple, but feature-rich tool to remotely control, manage,\nprovision and deploy your Matrix homeservers and users from your virtual\nterminal.\n\n```console\n$ matrixctl\nusage: matrixctl [-h] [--version] [-d] [-s SERVER] [-c CONFIG] Command ...\n\nMatrixCtl is a simple, but feature-rich tool to remotely control, manage, provision and deploy Matrix homeservers.\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --version             show program\'s version number and exit\n  -d, --debug           Enables debugging mode.\n  -s SERVER, --server SERVER\n                        Select the server. (default: "default")\n  -c CONFIG, --config CONFIG\n                        A path to an alternative config file.\n\nCommands:\n  The following are commands, you can use to accomplish various tasks.\n\n  Command\n    adduser             Add users to the homeserver\n    adduser-jitsi       Add users to a jitsi server\n    check               Checks the deployment with Ansible\n    delete-local-media  Delete cached (local) media that was last accessed before a\n                        specific point in time\n    delroom             Shutdown a room\n    deluser             Deactivate users\n    deluser-jitsi       Delete jitsi users\n    deploy              Provision and deploy the Ansible playbook\n    get-event           Get an event from the database\n    get-event-context   Get the context of an event\n    get-events          Get events from the database\n    is-admin            Check, if a user is a homeserver administrator\n    joinroom            Join a user to a room\n    maintenance         Run maintenance tasks\n    make-room-admin     Grant a user the highest power level available to a local user\n                        in this room\n    purge-history       Purge historic events from the database\n    purge-remote-media  Purge cached, remote media\n    report              Get a report event by report identifier\n    reports             Lists reported events\n    rooms               List rooms\n    server-notice       Send a server notice to a user\n    set-admin           Change whether a user is a homeserver admin or not\n    start               Starts all OCI containers\n    restart             Restarts all OCI containers (alias for start)\n    stop                Stop and disable all OCI containers\n    update              Updates the ansible playbook repository\n    upload              Upload a media file.\n    user                Get information about a specific user\n    users               Lists all users of the homeserver\n    version             Get the version information of the Synapse instance\n\nThank you for using MatrixCtl!\nCheck out the docs: https://matrixctl.rtfd.io\nReport bugs to: https://github.com/MichaelSasser/matrixctl/issues/new/choose\n```\n\n## Installation\n\nMatrixCtl is written in Python. The installation is straight forward. Just run\n`pip install matrixctl`. It will be installed from the\n[Python Package Index (PyPi)](https://pypi.org/project/matrixctl/).\n\nUpgrade MatrixCtl with `pip install --upgrade matrixctl`.\n\nYou will find more information in the\n[documentation](https://matrixctl.readthedocs.io/en/latest/installation.html).\n\n## Documentation\n\nThe [documentation](https://matrixctl.readthedocs.io/en/latest/index.html) is\nwaiting for you, to check out.\n\n## Configuration File\n\nTo use this tool you need to have a configuration file in\n"~/.config/matrixctl/config.yaml" or in "/etc/matrixctl/config.yaml".\n\n```yaml\n# Define your homeservers in "servers" here.\nservers:\n  # Your default server. You can specify muliple servers here with arbitrary\n  # Names\n  default:\n    ansible:\n      # The absolute path to your playbook\n      playbook: /path/to/ansible/playbook\n\n    synapse:\n      # The absolute path to the synapse playbook.\n      # This is only used for updating the playbook.\n      playbook: /path/to/synapse/playbook\n\n    # If your matrix server is deployed, you may want to fill out the API section.\n    # It enables matrixctl to run more and faster commands. You can deploy and\n    # provision your Server without this section. You also can create a user with\n    # "matrixctl adduser --ansible YourUsername" and add your privileges after\n    # that.\n    api:\n      # Your domain should be something like "michaelsasser.org" without the\n      # "matrix." in the front. MatrixCtl will add that, if needed. An IP-Address\n      # is not enough.\n      domain: example.com\n\n      # The username your admin user\n      username: johndoe\n\n      # To use the API you need to have an administrator account. Enter your Token\n      # here. If you use the element client you will find it your user settings\n      # (click on your username on the upper left corner on your browser) in the\n      # "Help & About" tab. If you scroll down click next to "Access-Token:" on\n      # "<click to reveal>". It will be marked for you. Copy it in here.\n      token: "MyMatrixToken"\n\n      # In some cases, MatrixCtl does need to make many requests. To speed those\n      # requests a notch, you can set a concurrent_limit which is greater than\n      # one. This sets a limit to how many asynchronous workers can be spawned\n      # by MatrixCtl. If you set the number to high, MatrixCtl needs more time\n      # to spawn the workers, then a synchronous request would take.\n      concurrent_limit: 10\n\n    # Here you can add your SSH configuration.\n    ssh:\n      address: matrix.example.com\n\n      # The default port is 22\n      port: 22\n\n      # The default username is your current login name.\n      user: john\n\n    # Define your maintenance tasks\n    maintenance:\n      tasks:\n        - compress-state # Compress synapses state table\n        - vacuum # VACUUM the synapse database (garbage-collection)\n\n    # Add connection parameters to the Database\n    # Synapse does only read (SELECT) information from the database.\n    # The user needs to be able to login to the synapse database\n    # and SELECT from the events and event_json tables.\n    database:\n      synapse_database: synapse # this is the playbooks default table name\n      synapse_user: matrixctl # the username (role) for the database\n      synapse_password: "RolePassword"\n      tunnel: true # true if an ssh tunnel should be used to connect\n\n      # The port that was used in the playbook  (e.g.\n      # matrix_postgres_container_postgres_bind_port: 5432)\n      # or for your external database. For security reasons the port\n      # should be blocked by your firewall. Iy you enable the tunnel\n      # by setting tunnel: true, MatrixCtl activates a SSH tunnel.\n      port: 5432 # the remote port\n\n  # Another server.\n  foo:\n    # ...\n```\n\nPredefined Jinja2 placeholders (all placeholders can be overwritten):\n\n- `"{{ home }}"` -- The current users home path e.g. `/home/michael`,\n- `"{{ user }}"` -- The current users username e.g. `michael`,\n- `"{{ default_ssh_port }}"` -- The default ssh port `22`,\n- `"{{ default_api_concurrent_limit }}"` -- The default concurrent limit `4`.\n\nCheck out the\n[documentation](https://matrixctl.readthedocs.io/en/latest/getting_started/config_file.html)\nfor more information.\n\n## Discussions & Chat\n\nIf you have any thoughts or questions, you can ask them in the\n[discusions](https://github.com/MichaelSasser/matrixctl/discussions) or in the\nprojects matrix room `#matrixctl:matrix.org`.\n\n## Semantic Versioning and Branching Model\n\nThis Python package uses [SemVer](https://semver.org/) for its release cycle\nand the\n[git-flow](https://danielkummer.github.io/git-flow-cheatsheet/index.html)\nbranching model (by [Vincent Driessen](https://nvie.com/about/)).\n\nIt has two branches with infinite lifetime. The:\n\n- [develop](https://github.com/MichaelSasser/matrixctl/tree/develop) branch is\n  the merging branch,\n- [master](https://github.com/MichaelSasser/matrixctl/tree/master) branch gets\n  updated on every release.\n\n## Contributing\n\nPlease check our\n[Contributer Documentation](https://matrixctl.readthedocs.io/en/latest/contributer_documentation/index.html#contributer-documentation).\n\n## License\n\nCopyright &copy; 2020-2001 Michael Sasser <Info@MichaelSasser.org>. Released\nunder the GPLv3 license.\n',
    'author': 'Michael Sasser',
    'author_email': 'Michael@MichaelSasser.org',
    'maintainer': 'Michael Sasser',
    'maintainer_email': 'Michael@MichaelSasser.org',
    'url': 'https://michaelsasser.github.io/matrixctl/index.html',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
