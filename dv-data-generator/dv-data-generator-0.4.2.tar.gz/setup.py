import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dv-data-generator",
    version="0.4.2",
    packages=setuptools.find_packages(),
    long_description_content_type="text/markdown",
    long_description=long_description,
    python_requires=">=3.8",
    install_requires=[
        "requests",
        "httplib2",
        "google-api-core",
        "google-api-python-client",
        "google-auth",
        "google-cloud-core",
        "google-resumable-media",
        "googleapis-common-protos",
        "google-auth-oauthlib",
        "oauth2client",
    ],
    url="https://gitlab.com/dqna/dv-data-generator",
)
