"""Setup configuration."""
import setuptools

with open("README.md", "r") as fh:
    LONG = fh.read()
setuptools.setup(
    name="aisapi",
    version="0.1.1",
    author="AI-Speaker",
    author_email="info@ai-speaker.com",
    description="",
    long_description=LONG,
    install_requires=["aiohttp", "async_timeout"],
    long_description_content_type="text/markdown",
    url="https://github.com/sviete/AIS-api",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
