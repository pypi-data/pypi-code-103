import setuptools
from setuptools import find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="CommercialScraper",
    version="0.0.2",
    author="Omar 4ldrich Tahmas",
    author_email="o.ismail@aol.co.uk",
    description="A dynamic and scalable data pipeline from Airbnbs commercial site to your local system / cloud storage.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BlairMar/Airbnb-webscraping-project",
    project_urls={
    
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # package_dir={"": "Pipeline"},
    # packages=setuptools.find_packages(where="Pipeline"),
    packages = find_packages(),
    install_requires= ["beautifulsoup4==4.10.0", "boto3==1.20.10", "botocore==1.22.8", "greenlet==1.1.2", "jmespath==0.10.0", "lxml==4.6.4", "numpy==1.21.4", "pandas==1.3.4", 'psycopg2==2.9.2', 'pytz==2021.3', 's3transfer==0.5.0', 'selenium==3.141.0', 'six==1.16.0', 'soupsieve==2.3.1', 'SQLAlchemy==1.4.27', 'urllib3==1.26.7']  ,

    python_requires=">=3.6"
)
