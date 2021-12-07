from setuptools import setup

"""
pip install --editable .
表示从本地或开发者模式安装项目，
-e, --editable <路径/网址>

521xiaoJIANG
"""

setup(
    name='gethome',
    version='0.1',
    py_modules=['hello'],
    install_requires=[
        'Click',
    ],
    entry_points={'console_scripts': [
        'digest=hello:hello',
        'goodbye=hello:gethome'
    ]},
)