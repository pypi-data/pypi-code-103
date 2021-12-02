import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytest-playwrights",
    author="liuxiankun",
    version="0.0.5",
    author_email="939449414@qq.com",
    description="A pytest wrapper with fixtures for Playwright to automate web browsers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/939449414/pytest-playwrights.git",
    packages=["pytest_playwright"],
    include_package_data=True,
    install_requires=[
        "playwright>=1.13",
        "pytest",
        "pytest-base-url",
        "python-slugify",
    ],
    entry_points={"pytest11": ["playwright = pytest_playwright.pytest_playwright"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Framework :: Pytest",
    ],
    python_requires=">=3.7",
    setup_requires=["setuptools_scm"],
)
