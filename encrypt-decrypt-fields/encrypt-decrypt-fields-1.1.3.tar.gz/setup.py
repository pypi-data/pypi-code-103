# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['encrypt_decrypt_fields']

package_data = \
{'': ['*']}

install_requires = \
['Django>=4.0,<5.0', 'SQLAlchemy>=1.4.19,<2.0.0', 'cryptography>=3.4.7,<4.0.0']

setup_kwargs = {
    'name': 'encrypt-decrypt-fields',
    'version': '1.1.3',
    'description': 'Encrypt and decrypt for django model field.',
    'long_description': "# ORM Encrypt Decrypt Fields\n \nA Django and SQLAlchemy model field that encrypts your data based SHA256 algorithm and Fernet (symmetric encryption) when saving to the model field.  The fernet module guarantees that data encrypted using it cannot be further manipulated or read without the key.  It keeps data always encrypted in the database.\n\nAlso, possible to use it directly with the Crypto class.\n\n[![Project Check](https://github.com/alpden550/django-encrypt-decrypt/actions/workflows/python-package.yml/badge.svg)](https://github.com/alpden550/django-encrypt-decrypt/actions/workflows/python-package.yml)\n\n## How install\n\n```\npip install encrypt-decrypt-fields\n```\n\n## Usage\n\nFor Django use project secret key or own:\n\n```\nfrom django.conf import settings\nfrom django.db import Model\nfrom django_encrypt_decrypt import EncryptedBinaryField\n\n\nclass DemoModel(models.Models):\n    password = EncryptedBinaryField(blank=True, null=True)\n```\n\n```\nDemoModel.objects.create(password='password')\n```\n\n```\nobj = DemoModel.objects.get(id=1)\nobj.password.to_bytes()  # b'gAAAAABgxGVVeTPV9i1nPNl91Ss4XVH0rD6eJCgOWIOeRwtagp12gBJg9DL_HXODTDW0WKsqc8Z9vsuHUiAr3qQVE9YQmTd3pg=='\n```\n\nTo read bytes in postgres, use to_bytes() method of memoryview\n\n```\nobj.password.to_bytes()\n```\n\nor\n\n```\nbytes(obj.password, 'utf-8')\n```\n\nTo decrypt value use Crypto class:\n\n```\nfrom django.conf import settings\nfrom django_encrypt_decrypt import Crypto\n\nobj = DemoModel.objects.get(id=1)\n\ndecrypted = Crypto(settings.SECRET_KEY).decrypt_token(obj.password.to_bytes())\ndecrypted  # 'password'\n```\n\nFor SQLAlchemy, it is similar:\n\n```\nfrom sqlalchemy import create_engine\nfrom sqlalchemy.orm import declarative_base\nfrom sqlalchemy import Column, Integer, String\n\nBase = declarative_base()\n\n\nclass Demo(Base):\n    __tablename__ = 'demo'\n\n    id = Column(Integer, primary_key=True)\n    name = Column(String)\n    password = Column(EncryptedAlchemyBinaryField(key='secret), nullable=True)\n```\n\n```\nobject = session.query(Demo).first()\nCrypto('secret').decrypt_token(object.password)  \n```\n",
    'author': 'Denis Novikov',
    'author_email': 'alpden550@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/alpden550/django-encrypt-decrypt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
