from setuptools import setup, find_packages
from gunicorn_logger import __version__

setup(
    name="gunicorn-json-logger",
    version=__version__,
    url="https://github.com/wahlandcase/gunicorn-json-logger/",
    license="MIT",
    description="Json log configuration for Gunicorn+Uvicorn",
    long_description="JSON log configuration for Gunicorn+Uvicorn",
    long_description_content_type="text/plain",
    author="Melvin Koh",
    author_email="melvinkcx@gmail.com",
    packages=find_packages(),
    install_requires=[
        "python-json-logger>=2.0"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: System :: Logging",
    ]
)
