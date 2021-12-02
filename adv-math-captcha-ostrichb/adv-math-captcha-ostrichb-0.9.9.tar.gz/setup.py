import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="adv-math-captcha-ostrichb",
    version="0.9.9",
    author="Ostrichbeta",
    author_email="ostrichb@yandex.com",
    description="Advanced mathematical captcha generator and ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ostrichbeta/adv-math-captcha",
    project_urls={
        "Bug Tracker": "https://github.com/Ostrichbeta/adv-math-captcha/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "sympy>=1.9"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
)