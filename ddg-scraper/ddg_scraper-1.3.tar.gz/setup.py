from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="ddg_scraper",
    version="1.3",
    packages=find_packages(include=["ddg_scraper", "ddg_scraper.*"]),
    install_requires=['selectolax', 'yarl', 'httpx'],
    author="Myxi",
    author_email="myxi@duck.com",
    url="https://github.com/m-y-x-i/duckduckgo-scraper",
    description="Easy to use asynchronous and synchronous DuckDuckGo search engine scraper.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    license="GNU GPLv3",
)