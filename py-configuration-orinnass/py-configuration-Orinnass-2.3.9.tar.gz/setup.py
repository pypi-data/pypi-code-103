"""
Пакет установки модуля
"""
from setuptools import setup
from setuptools import find_packages
from config import __version__, __name__


def get_install_requires():
    """
    Метод получения зависимых модулей
    """
    with open('requirements.txt', 'r') as file_req:
        lines_req = file_req.readlines()
        for index, i in enumerate(lines_req):
            if '-e' in i:
                module_name = i.split('#egg=')[1].strip()
                install_command = i.split('-e ')[1].strip()
                lines_req[index] = f'{module_name} @ {install_command}\n'
            else:
                lines_req[index] = lines_req[index].replace('==', '>=')
        return lines_req


setup(
    name=__name__,
    version=__version__,
    download_url="https://gitlab.com/Orinnass/python-module-configuration",
    packages=find_packages(include=('config', 'template_config.json'), exclude=('test',)),
    scripts=['config_cli.py'],
    install_requires=get_install_requires(),
    python_requires=">=3.10"
)
