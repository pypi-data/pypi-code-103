import setuptools 
setuptools.setup (
    name = "wifiqr",
    version="1.2.5",
    author="Pyae Phyo Hein",
    author_email="pyaephyohein.info.3326@gmail.com",
    descripton="Wifi Qr creater and generator for linux",
    packages=["wifiqr"],
    entry_points = {
        'console_scripts' : ['wifiqr=wifiqr.wifiqr:wifiqr']
    },
    install_requires=[
        'qrcode'
    ]
    )
