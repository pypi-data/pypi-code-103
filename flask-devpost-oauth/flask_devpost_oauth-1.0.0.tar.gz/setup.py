import setuptools

with open("README.md", "r") as fhandle:
    long_description = fhandle.read()

setuptools.setup(
    name="flask_devpost_oauth",
    version="1.0.0",
    author="EpicCodeWizard",
    author_email="epiccodewizard@gmail.com",
    description="Brings DevPost OAuth to Flask.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://replit.com/@EpicCodeWizard/Flask-Devpost-OAuth-Extension",
    packages=setuptools.find_packages(),
    install_requires=[
        "Flask==2.0.2",
        "gunicorn==20.1.0",
        "eventlet==0.33.0",
        "gevent-websocket",
        "python-socketio==4.6.0",
        "python-engineio==3.13.2",
        "Flask-SocketIO==4.3.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)