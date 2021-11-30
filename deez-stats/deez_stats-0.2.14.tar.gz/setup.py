import pathlib
from setuptools import setup, find_packages


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


setup(
    name='deez_stats',
    version='0.2.14',
    author='Tom Brady',
    author_email='bradyte@gmail.com',
    description='Python bindings to access competitive league stats.',
    license='MIT',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/salty-spitoon/deez_stats',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=['objectpath', 'yahoo_fantasy_api', 'yahoo_oauth', 'numpy', 'pandas'],
    python_requires='>=3.7.1,<3.11'
)
