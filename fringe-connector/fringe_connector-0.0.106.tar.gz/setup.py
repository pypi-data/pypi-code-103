import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fringe_connector",
    version="0.0.106",
    author="Rene Serulle",
    author_email="rene@insomnyak.com",
    description="Suite of prebuilt connectors to other APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/insomnyak-connector/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha"
    ],
    python_requires='>=3.7.3',
    keywords='gcp gsuite gmail gsheets bigquery gdrive',
    install_requires=['numpy', 'pandas', 'google-api-python-client', 'google-auth-httplib2', 'google-auth-oauthlib', 'google-cloud-storage', 'google-cloud-bigquery', 'google-cloud-bigquery-storage', 'selenium']
)
