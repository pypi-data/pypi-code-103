from setuptools import setup, find_packages


with open("README.md", "r") as f:
    README = f.read()


REQUIREMENTS = (
    "requests>=2.26,<3",
    "beautifulsoup4>=4.10,<5",
    "lxml>=4.6,<5",
)


setup(
    name="cfapi",
    version="1.0.0",
    description="An unofficial Codeforces API, that gives you access to contests, problems, and profiles on Codeforces.com",
    author="RealA10N",
    author_email="downtown2u@gmail.com",
    url="https://github.com/RealA10N/cfapi",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords="Codeforces Codeforces.com Competitive Programming API Wrapper Scraper",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=REQUIREMENTS,
)
