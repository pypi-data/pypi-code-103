# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['obserware',
 'obserware.commons',
 'obserware.readers',
 'obserware.readers.cputwind',
 'obserware.readers.cyclwind',
 'obserware.readers.lgptwind',
 'obserware.readers.mainwind',
 'obserware.readers.ntwkwind',
 'obserware.readers.phptwind',
 'obserware.readers.procwind',
 'obserware.readers.sostwind',
 'obserware.screens',
 'obserware.screens.cputwind',
 'obserware.screens.cyclwind',
 'obserware.screens.lgptwind',
 'obserware.screens.mainwind',
 'obserware.screens.ntwkwind',
 'obserware.screens.phptwind',
 'obserware.screens.procwind',
 'obserware.screens.sostwind',
 'obserware.widgets',
 'obserware.widgets.cyclwdgt']

package_data = \
{'': ['*'],
 'obserware': ['assets/fonts/*', 'assets/images/*', 'assets/uifiles/*']}

install_requires = \
['distro>=1.6.0,<2.0.0',
 'psutil>=5.8.0,<6.0.0',
 'py-cpuinfo>=8.0.0,<9.0.0',
 'pyqt5>=5.15.6,<6.0.0',
 'pyqtchart>=5.15.5,<6.0.0']

entry_points = \
{'console_scripts': ['obserware = obserware.main:main']}

setup_kwargs = {
    'name': 'obserware',
    'version': '0.2.2',
    'description': 'An advanced system monitor utility written in Python and Qt',
    'long_description': '# Obserware\n\nAn advanced system monitor utility written in Python and Qt\n\n## Installation\n\n### Development\n\n1. `sudo dnf install python3-poetry`\n2. `git clone https://gitlab.com/t0xic0der/obserware.git`\n3. `cd obserware`\n4. `virtualenv venv`\n5. `source venv/bin/activate`\n6. `poetry install`\n7. `deactivate`\n\n### Consumption\n\n1. `virtualenv venv`\n2. `source venv/bin/activate`\n3. `pip3 install obserware`\n4. `deactivate`\n\n## Usage\n\n1. `source venv/bin/activate`\n2. `obserware`\n3. `deactivate`\n\n## Screenshots\n\n1. **Windows**  \n   1. _Performance tabscreen_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_mainperf.png  \n      ![](screenshots/obsr_mainperf.png)\n   2. _Processes tabscreen_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_mainproc.png  \n      ![](screenshots/obsr_mainproc.png)\n   3. _Information tabscreen_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_maininfo.png  \n      ![](screenshots/obsr_maininfo.png)\n   4. _Contribute tabscreen_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_maincntb.png  \n      ![](screenshots/obsr_maincntb.png)\n2. **Dialogs**  \n   1. _CPU cycles dialog_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_cyclwind.png  \n      ![](screenshots/obsr_cyclwind.png)\n   2. _CPU times dialog_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_cputwind.png  \n      ![](screenshots/obsr_cputwind.png)\n   3. _Storage counters dialog_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_sostwind.png  \n      ![](screenshots/obsr_sostwind.png)\n   4. _Network statistics dialog_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_ntwkwind.png  \n      ![](screenshots/obsr_ntwkwind.png)\n   5. _Physical partitions dialog_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_phptwind.png  \n      ![](screenshots/obsr_phptwind.png)\n   6. _Logical partitions dialog_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_lgptwind.png  \n      ![](screenshots/obsr_lgptwind.png)\n   7. _Process information dialog_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_procwind.png  \n      ![](screenshots/obsr_procwind.png)\n',
    'author': 'Akashdeep Dhar',
    'author_email': 'akashdeep.dhar@gmail.com',
    'maintainer': 'Akashdeep Dhar',
    'maintainer_email': 'akashdeep.dhar@gmail.com',
    'url': 'https://gitlab.com/t0xic0der/obserware',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
