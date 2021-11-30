import setuptools


def long_description() -> str:
    with open("README.md", "r", encoding="utf8") as f:
        return f.read()


setuptools.setup(
    name="gemtide",
    version="0.1.1",
    url="https://git.sr.ht/~supergrizzlybear/gemtide",
    license="Other/Proprietary License",
    author="supergrizzlybear",
    author_email="supergrizzlybear@protonmail.com",
    description="A Jetforce application for serving information about UK tidal events over the Gemini Protocol",
    install_requires=[
    	"jetforce",
    	"aiohttp",
    	"ukhotides",
    	"jinja2",
    	"unicode-slugify",
    	"pyyaml"
    ],
    long_description=long_description(),
    long_description_content_type="text/markdown",
    packages=["gemtide"],
    package_data={"gemtide": ["templates/*"]},
    entry_points={
        "console_scripts": [
            "gemtide=gemtide.__main__:main"
        ]
    },
    python_requires=">=3.7",
    keywords="gemini",
    classifiers=[
	    "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False
)
