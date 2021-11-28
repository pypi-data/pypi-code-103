import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vpscli",
    version="0.0.6dev2",
    author="slipper",
    author_email="r2fscg@gmail.com",
    description="VPS manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GaoangLiu/vpsinit",
    packages=setuptools.find_packages(),
    install_requires=['endlessh', 'codefast','joblib', 'argparse'],
    entry_points={'console_scripts': ['vpsinit=vps.__init__:main']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
