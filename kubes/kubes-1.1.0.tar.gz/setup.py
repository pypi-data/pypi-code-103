from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='kubes',
    version='1.1.0',
    author='Ron Chang',
    author_email='ron.hsien.chang@gmail.com',
    description=(
        'To take care kubectl command'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Ron-Chang/kubes.git',
    packages=find_packages(),
    license='MIT',
    python_requires='>=3.6',
    exclude_package_date={'':['.gitignore', 'setup.py']},
    scripts=['bin/kubes'],
)

