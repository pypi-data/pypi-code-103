import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mrl-airsim",
    version="0.0.4",
    author="Stefan Wapnick",
    author_email="stefan.wapnick@mail.mcgill.ca",
    description="Fork of AirSim developped by McGill MRL (Mobile Robotics Lab). Original credit goes to Microsoft AI & Research for development of the AirSim package.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/microsoft/airsim",
    packages=setuptools.find_packages(),
	license='MIT',
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
          'msgpack-rpc-python', 'numpy', 'opencv-contrib-python'
    ]
)
