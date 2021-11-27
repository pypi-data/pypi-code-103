import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="machdi",
    version="0.0.1.4.dev2",
    author="Mahdi Zare",
    author_email="thisismahdizare@gmail.com",
    description="machdi is an open source machine learning module that provides create ML models, preprocessing algorithms and evaluation metrics. this project is developing.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ThisIsMahdiZare/machdi",
    project_urls={
        "Bug Tracker": "https://github.com/ThisIsMahdiZare/machdi/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=['numpy','matplotlib']
)