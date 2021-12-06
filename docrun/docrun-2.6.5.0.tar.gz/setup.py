import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

    setuptools.setup(
        name="docrun",
        version="2.6.5.0",
        author="Xiao, Hu",
        author_email="service@ovo.ltd",
        description="Package for https://doc.run",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://doc.run",
        packages=setuptools.find_packages(),
        install_requires=[
            'websockets',
            'paramiko',
            'psutil',
            'ipykernel',
            'matlab-kernel',
            'powershell_kernel',
            'bash_kernel',
        ],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
