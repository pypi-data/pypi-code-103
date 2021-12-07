import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dv-mock-api",
    version="0.1.0",
    packages=setuptools.find_packages(),
    long_description_content_type="text/markdown",
    long_description=long_description,
    python_requires=">=3.8",
    install_requires=[
        "flask",
        "faker",
        "requests",
        "httplib2",
        "google-api-core",
        "google-api-python-client",
        "google-auth",
        "google-cloud-core==1.3.0",
        "google-resumable-media==0.5.0",
        "googleapis-common-protos==1.51.0",
        "google-auth-oauthlib==0.4.1",
        "oauth2client==4.1.3"
    ],
    include_package_data=True,
    url="https://gitlab.com/dqna/DV360-mock-api",
)
