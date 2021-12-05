import os
import setuptools

src_files = os.listdir("src/hcs_grpc_client")
version = "0.20.0"  # keep track of 'hedera-protobufs' version

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hcs-grpc-client",
    version=version,
    author="Wensheng Wang",
    author_email="wenshengwang@gmail.com",
    description="Hedera HCS gRPC API Python Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wensheng/hcs-grpc-api-py-client",
    project_urls={
        "Bug Tracker": "https://github.com/wensheng/hcs-grpc-api-py-client/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=['grpcio>=1.38.1',
                      'protobuf>=3.17.3'],
    python_requires=">=3.6",
)
