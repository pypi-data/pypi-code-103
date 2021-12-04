from setuptools import find_packages
from setuptools import setup
from pathlib import Path

setup(
    name="color-detection-jdla",
    version="0.0.2",
    py_modules=["color_detection"],
    description="Color Detection using OpenCV",
    long_description_content_type="text/markdown",
    long_description=Path("README.md").read_text(),
    author="Josué de León",
    author_email="josuedlavs@gmail.com",
    url="https://github.com/JosueDLA/ColorDetection",
    license='MIT',
    packages=find_packages(exclude=["colors.py"]),
    install_requires=[
        "numpy==1.21.4",
        "opencv-python==4.5.4.60",
        "colorthief==0.2.1",
        "pillow==8.4.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
