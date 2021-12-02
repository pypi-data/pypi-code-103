from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as rm:
    readme = rm.read()

setup(
    name='squarecloud',
    packages=find_packages(),
    version='1.3',
    license='Apache-2.0',
    description='Este módulo foi desenvolvido com o intuito de auxiliar as pessoas de coletar informações relacionadas as suas aplicações hospedadas na https://squarecloud.app!',
    author='NemRela',
    url='https://github.com/squarecl/square-python-status',
    project_urls={
        'Bug Hunter': 'https://github.com/squarecl/square-python-status/issues',
        'Documentation': 'https://github.com/squarecl/square-python-status'
    },
    keywords=[
        'squarecloud',
        'square cloud',
        'square-python-status',
        'square'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: POSIX :: Linux'
    ],
    long_description=readme,
    long_description_content_type='text/markdown',
    python_requires='>=3.6.0'
)
