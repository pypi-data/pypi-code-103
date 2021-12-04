from setuptools import setup, find_packages
import os

VERSION = '0.9.3'
DESCRIPTION = 'The open-world, OpenGL video game made in Python'
LONG_DESCRIPTION = 'The open-world, OpenGL video game made in Python, this project is still in development, but feel free to give it a go! For more information we recommend you check out the README here: https://github.com/PycraftDeveloper/Pycraft'
base_folder = os.path.dirname(__file__)
README = open("README.md", "r").read()

# Setting up
setup(
    name="Python-Pycraft",
    version=VERSION,
    author="PycraftDev (Tom Jebbo)",
    author_email="<thomasjebbo@gmail.com>",
    url="https://github.com/PycraftDeveloper/Pycraft",
    description=DESCRIPTION,
    long_description_content_type='text/markdown',
    long_description=README,
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Pillow", "Pygame", "PyOpenGL", "PyOpenGL-Accelerate", "Moderngl", "Moderngl-window", "Numpy", "PyAutoGUI", "Psutil", "PyWaveFront", "Py-Cpuinfo", "Gputil", "Tabulate"],
    keywords=['python', "pillow", "pygame", "pyopengl", "pyopengl-accelerate", "numpy", "gputil" "py-cpuinfo", "pywavefront", "psutil", "pyautogui", "tabulate", "OpenGL", "khronos", "pycraftDev", "game", "3D", "Openworld"],
    classifiers=[
        "Intended Audience :: Other Audience",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Games/Entertainment"
    ]
)
