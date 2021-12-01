import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="discordsrv_api",
    version="0.2.6",
    description="UUID to Discord ID converter for Minecraft and discordsrv",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.cofob.ru/cofob/discordsrv_api",
    install_requires=["mysql-connector-python"],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
