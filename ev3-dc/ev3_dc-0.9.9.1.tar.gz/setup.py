import setuptools
import platform

with open("README.rst", "r") as fh:
    long_description = fh.read()

if platform.system() == 'Darwin':
    install_requires = [
        'thread_task >= 0.9.7',
        'gTTS',
        'hidapi'
    ]
else:
    install_requires = [
        'thread_task >= 0.9.7',
        'gTTS',
        'pyusb'
    ]


setuptools.setup(
    name="ev3_dc",
    version="0.9.9.1",
    author="Christoph Gaukel",
    author_email="christoph.gaukel@gmx.de",
    description="EV3 direct commands",
    long_description=long_description,
    url="https://github.com/ChristophGaukel/ev3-python3",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.3',
    install_requires=install_requires
)
