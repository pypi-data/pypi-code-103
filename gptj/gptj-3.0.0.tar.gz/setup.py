from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as gpt:
    long_description = gpt.read()

VERSION = '3.0.0'
DESCRIPTION = 'A GPT-J api to use with python3 to generate text, blogs, code, and more (Note: Starting with version 3.0.0, the API uses a different domain to generate text with GPT-J and features such as max length have been removed)'

setup(name="gptj",
    version=VERSION,
    author="TheProtagonist (Michael Arana)",
    author_email="MichaelGamer256@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/TheProtaganist/gpt-j",
    py_modules=["Basic_api", "Gptj", "gpt_api", "ImaginaryFriend", "security", "Text2TextGen"],
    license="MIT",
    long_description=long_description,
    packages=find_packages(),
    package_dir={" ": "gpt_j"},
    install_requires=['requests', 'ProfanityDetector', 'cryptography'],
    keywords=['python', 'text generation', 'chatbot framework', 'gpt-J', 'gpt-3', 'gpt-2', 'completion', 'code completion', 'language models', 'language model', 'nlp', 'natural language', 'natural language processing', 'meta-programming', 'story generation', 'story', 'API'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
