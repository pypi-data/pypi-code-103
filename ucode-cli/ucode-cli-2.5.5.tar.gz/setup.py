from setuptools import setup, find_packages

with open('README.md', encoding="utf-8") as readme_file:
    README = readme_file.read()

with open('HISTORY.md', encoding="utf-8") as history_file:
    HISTORY = history_file.read()
# HISTORY = ""

setup_args = dict(
    name='ucode-cli',
    version='2.5.5',
    description='CLI tools to prepare problems locally and to work with ucode.vn server',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(exclude=('tests', )),
    include_package_data=True,
    author='Thuc Nguyen',
    author_email='gthuc.nguyen@gmail.com',
    keywords=['ucode', 'ucode CLI tools'],
    url='https://gitlab.com/ucodevn/ucode-cli',
    download_url='https://pypi.org/project/ucode/',
    # py_modules=['firestoretools'],
    entry_points='''
        [console_scripts]
        ucode=ucode.cli.main:app
    ''',
)

install_requires = [
    'click',
    'requests',
    'beautifulsoup4',
    'tomd',
    'jinja2',
    'dataclasses-json',
    'unidecode',
    'typer',
    'colorama',
    'ruamel.yaml',
    'pysimplegui'
]


if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
