import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="munibot_es",
    version="0.0.3",
    author="Adrià Mercader",
    author_email="amercadero@gmail.com",
    description="A Twitter bot built with munibot that tweets aerial imagery pictures of Spain municipalities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amercader/munibot_es",
    packages=setuptools.find_packages(),
    install_requires=["munibot"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "munibot_profiles": [
            "es=munibot_es.profiles.es:MuniBotEs",
            "cat=munibot_es.profiles.cat:MuniBotCat",
        ],
    },
)
