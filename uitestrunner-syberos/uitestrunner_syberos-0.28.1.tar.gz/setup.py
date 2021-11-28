from setuptools import setup, find_packages
setup(
    name='uitestrunner_syberos',
    version='0.28.1',
    author='Jinzhe Wang',
    description='A ui automated testing tool for SyberOS',
    author_email='wangjinzhe@syberos.com',
    url='http://www.syberos.cn/',
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=["uitestrunner_syberos.Device",
                "uitestrunner_syberos.Item",
                "uitestrunner_syberos.Connection",
                "uitestrunner_syberos.Events",
                "uitestrunner_syberos.Watcher",
                "uitestrunner_syberos.setup",
                "uitestrunner_syberos.__main__"],
    package_data={
        "uitestrunner_syberos": ["data/server.sop"]
    },
    install_requires=["sseclient",
                      "paramiko",
                      "scp",
                      "lxml",
                      "urllib3",
                      "opencv-python",
                      "numpy",
                      "psutil",
                      "sympy"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6, <4"
)
