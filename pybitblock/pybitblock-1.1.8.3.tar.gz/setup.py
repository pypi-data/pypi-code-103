# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pybitblock', 'pybitblock.grpc_generated', 'pybitblock.terminal_matrix']

package_data = \
{'': ['*'],
 'pybitblock': ['config/bclock.conf',
                'config/bclock.conf',
                'config/bclock.conf',
                'config/init.conf',
                'config/init.conf',
                'config/init.conf',
                'config/selection.conf',
                'config/selection.conf',
                'config/selection.conf',
                'images/*',
                'resources/images/*']}

install_requires = \
['Pillow>=8.4.0,<9.0.0',
 'art>=5.3,<6.0',
 'certifi>=2021.10.8,<2022.0.0',
 'chardet>=4.0.0,<5.0.0',
 'googleapis-common-protos==1.52.0',
 'grpcio>=1.42.0,<2.0.0',
 'idna>=3.3,<4.0',
 'lnpay-py>=0.1.0,<0.2.0',
 'numpy>=1.21.4,<2.0.0',
 'pdfminer>=20191125,<20191126',
 'protobuf==3.13.0',
 'psutil>=5.8.0,<6.0.0',
 'pycoingecko>=2.2.0,<3.0.0',
 'python-cfonts>=1.5.2,<2.0.0',
 'python-gnupg>=0.4.7,<0.5.0',
 'qrcode>=7.3.1,<8.0.0',
 'requests>=2.26.0,<3.0.0',
 'robohash>=1.1,<2.0',
 'simplejson>=3.17.6,<4.0.0',
 'six==1.15.0',
 'sseclient-py>=1.7.2,<2.0.0',
 'termcolor>=1.1.0,<2.0.0',
 'typer>=0.4.0,<0.5.0',
 'urllib3>=1.26.7,<2.0.0',
 'xmltodict>=0.12.0,<0.13.0']

entry_points = \
{'console_scripts': ['pyblock = pybitblock.console:main']}

setup_kwargs = {
    'name': 'pybitblock',
    'version': '1.1.8.3',
    'description': 'Python Bitcoin block dashboard, transactions, send message to Space and more',
    'long_description': '<img src="./pybitblock/resources/images/Logo.PNG" width="80%" />\n\n   \n    ----------------------\n    CPU Usage: X% \n    Memory Usage: X% \n    ----------------------\n\t\n    Local: PyBLOCK\n    Node:  XxXxXxX\n    Block: XxXxXxX\n    Version: X.x.X\n    \n    A. PyBLOCK\n    B. Bitcoin Core\n    L. Lightning Network\n    P. Platforms\n    S. Settings\n    X. Donate\n    Q. Exit\n    \n    Select option:     \n\n\n<br />\n\n<img src="https://pbs.twimg.com/media/Entgg9HXEAI6yea.jpg" width="50%" />\n\n<br />\n\n<img src="https://pbs.twimg.com/media/EpYxp_oWEAE88s-.jpg" width="50%" />\n\n<br />\n\n<img src="https://pbs.twimg.com/media/E5VnuZYXIAAVlVh.jpg" width="50%" />\n\n<br />\n\n<img src="https://pbs.twimg.com/media/FDBefZPWQAQDEVo.jpg" width="50%" />\n\n<br />\n\n<img src="https://pbs.twimg.com/media/FAskRpLXIAgC-fC.jpg" width="50%" />\n\n<br />\n\n<img src="https://pbs.twimg.com/media/FADnL4DXoAIlkwR.jpg" width="50%" />\n\n# PyBlock v1.1.8.2\nℙ𝕪𝔹𝕃𝕆ℂ𝕂 𝕚𝕥𝕤 𝕒 𝔹𝕚𝕥𝕔𝕠𝕚𝕟 𝔻𝕒𝕤𝕙𝕓𝕠𝕒𝕣𝕕 𝕨𝕚𝕥𝕙 ℂ𝕪𝕡𝕙𝕖𝕣𝕡𝕦𝕟𝕜 𝕒𝕖𝕤𝕥𝕙𝕖𝕥𝕚𝕔.\n\n- This will fully work on a Node that has Bitcoin Core and LND installed.\n- We fully tested and worked perfect on [MyNodeBTC](https://twitter.com/_PyBlock_/status/1402516068959199233)\n- We fully tested and worked perfect on [RaspiBlitz](https://twitter.com/_PyBlock_/status/1405788110458441728)\n- We fully tested and worked perfect on [BitcoinMachines](https://twitter.com/_PyBlock_/status/1365757861217861632)\n- We fully tested and worked perfect on [Umbrel](https://twitter.com/_PyBlock_/status/1405574038320201733)\n\n# First Start\n\n- You will need to find the path of the files tls.cert and admin.macaroon to do the REST connection to have access to LND.\n- [Poetry](https://python-poetry.org/) is needed to ensure every user has the same python dependencies installed.\n\n    ### From LOCAL Node\n\n    Open the Terminal.\n\n    -- Easy mode:\n    * a@A:~> sudo apt install hexyl\n    * a@A:~> pip3 install pybitblock\n    * a@A:~> pyblock\n    \n    -- Manual mode:\n    * a@A:~> sudo apt install hexyl\n    * a@A:~> pip3 install poetry\n    * a@A:~> git clone https://github.com/curly60e/pyblock.git\n    * a@A:~> cd pyblock\n    * a@A:~> poetry install\n    * a@A:~> poetry run python3 PyBlock.py\n\n    -- Upgrade:\n    * a@A:~> pip3 install pybitblock -U\n    * a@A:~> pyblock\n\n    <br />\n\n    - This is how we continue.\n\n    <br />\n\n    <img src="./pybitblock/resources/images/REST1.PNG" width="30%" />\n\n    <br />\n\n    - It will ask you for the IP:PORT (REST PORT) in this case use: localhost instead of the IP.\n\n    <br />\n\n    <img src="./pybitblock/resources/images/REST2.PNG" width="30%" />\n\n    <br />\n\n    - Then it will ask you for the path to the tls.cert.\n\n    <br />\n\n    <img src="./pybitblock/resources/images/REST3.PNG" width="30%" />\n\n    <br />\n\n    - Then it will ask you for the path to the admin.macaroon.\n\n    <br />\n\n    <img src="./pybitblock/resources/images/REST4.PNG" width="30%" />\n\n    <br />  \n\n    - Then it will ask you for the path to bitcoin-cli or if you have already installed just put: bitcoin-cli.\n\n    <br />\n\n    <img src="./pybitblock/resources/images/bitcoin-cli.PNG" width="30%" />\n\n    <br />\n\n    - And you are in.\n\n    <br />\n\n    <img src="./pybitblock/resources/images/main.PNG" width="30%" />\n\n    <br />\n\n    ### From REMOTE Computer\n\n    * You will need to have tls.cert and admin.macaroon already downloaded from your LND node.\n    * [Poetry](https://python-poetry.org/) is needed to ensure every user has the same python dependencies installed.\n\n     - Open the Terminal\n     \n\t    -- Easy mode:\n\t    * a@A:~> sudo apt install hexyl\n\t    * a@A:~> pip3 install pybitblock\n\t    * a@A:~> pyblock\n\n\t    -- Manual mode:\n\t    * a@A:~> sudo apt install hexyl\n\t    * a@A:~> pip3 install poetry\n\t    * a@A:~> git clone https://github.com/curly60e/pyblock.git\n\t    * a@A:~> cd pyblock\n\t    * a@A:~> poetry install\n\t    * a@A:~> poetry run python3 PyBlock.py\n\n\t    -- Upgrade:\n\t    * a@A:~> pip3 install pybitblock -U\n\t    * a@A:~> pyblock\n\n        <br />\n\n        - This is how we continue.\n\n        <br />\n\n        <img src="./pybitblock/resources/images/REST1.PNG" width="30%" />\n\n        <br />\n\n        - It will ask you for the IP:PORT (REST PORT).\n\n        <br />\n\n        <img src="./pybitblock/resources/images/REST1REMOTE.PNG" width="30%" />\n\n        <br />\n\n        - Then it will ask you for the path to the tls.cert.\n\n        <br />\n\n        <img src="./pybitblock/resources/images/REST2REMOTE.PNG" width="30%" />\n\n        <br />\n\n        - Then it will ask you for the path to the admin.macaroon.\n\n        <br />\n\n        <img src="./pybitblock/resources/images/REST3REMOTE.PNG" width="30%" />\n\n        <br />  \n\n        - Then it will ask you for the path to bitcoin-cli or if you have already installed just put: bitcoin-cli.\n\n        <br />\n\n        <img src="./pybitblock/resources/images/bitcoin-cli.PNG" width="30%" />\n\n        <br />\n\n        - And you are in.\n\n        <br />\n\n        <img src="./pybitblock/resources/images/main.PNG" width="30%" />\n\n        <br />\n\n\n## Dependencies\n\n  - Install Curl on Debian based type:\n    - sudo apt install curl\n\n## How to execute\n\n  - python3 PyBlock.py\n\n\n### Tools by\n\n[@Curly60e](https://twitter.com/royalfield370) ⚡️ curly60e@bitrefill.com\n\n[@SamouraiDev,](https://twitter.com/SamouraiDev)\n[@Korynewton,](https://twitter.com/kn3wt)\n[@Tippin_Me,](https://twitter.com/tippin_me)\n[@TallyCoinApp,](https://twitter.com/tallycoinapp)\n[@MemPool,](https://twitter.com/mempool)\n[@CoinGecko,](https://twitter.com/coingecko)\n[@Igor_Chubin,](https://twitter.com/igor_chubin)\n[@Shesek,](https://twitter.com/shesek)\n[@LNBits,](https://twitter.com/lnbits)\n[@LNPAYco,](https://twitter.com/LNPAYco)\n[@OpenNodeCo,](https://twitter.com/OpenNodeCo)\n[@BlockStream,](https://twitter.com/Blockstream)\n[@Gwidion,](https://twitter.com/gwidion)\n[@AlphaaZeta,](https://twitter.com/alphaazeta)\n[@Hampus_S,](https://twitter.com/hampus_s)\n[@Mutatrum,](https://twitter.com/mutatrum)\n[@RoboHash,](https://twitter.com/Robohash)\n[@C_Otto83,](https://twitter.com/c_otto83)\n[@BashCo_,](https://twitter.com/BashCo_)\n[@JamesOb,](https://twitter.com/jamesob)\n[@BenTheCarman,](https://twitter.com/benthecarman)\n[@Whale_Alert,](https://twitter.com/whale_alert)\n[@Danvergara...](https://twitter.com/__danvergara__)\n\nSUPPORT PyBLØCK.\n\nBitcoin Address: bc1qjzaz34nv2ev55vfdu9m5qh0zq0fwcn6c7pkcrv\n\n<img src="/pybitblock/images/bitcoin-donation.png" width="30%" />\n\nSamourai Wallet Paynym: PM8TJhNTTq3YVocXuPtLjKx7pKkdUxqwTerWJ2j2a7dNitgyMmBPN6gK61yE17N2vgvQvKYokXktt6D6GZFTmocvDJhaUJfHt7ehEMmthjsT3NQHseFM\n\n<img src="/pybitblock/images/codeimage.png" width="30%" />\n\nMonero: 42jtb4dAfm6BQ8h6x56qGyAMMHVXGRwRMTSb2LwsBg1jVqD4TxfpD1pTK56tkrTMGhEKipZdDHfJrB1g8iQfvSyC7gZ9M8M\n\n<img src="/pybitblock/images/qrcode.png" width="20%" />\n',
    'author': 'curly60e',
    'author_email': 'curly60e@piserver.xyz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/curly60e/pyblock',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
