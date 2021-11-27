from pathlib import Path
from setuptools import setup, find_packages


setup(
    name="pytest-db-plugin",
    author="Avi Naftalis",
    author_email="avin@hailo.ai",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["pytest>=5.0"],
    extras_require={"es": "elasticsearch"},
    entry_points={"pytest11": ["db = pytest_db.plugin"]},
    python_requires=">=3.6",
    version="0.0.0.0.0.2",
    classifiers=[
        "Framework :: Pytest",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
)
