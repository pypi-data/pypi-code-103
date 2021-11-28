import codefast as cf
import setuptools

setuptools.setup(
    name="dofast",
    version="0.8.8dev2",  # Latest version .
    author="GaoangLiu",
    author_email="byteleap@gmail.com",
    description="A package for dirty faster Python programming.",
    long_description=open('README.md', 'r').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/GaoangLiu/slipper",
    packages=setuptools.find_packages(),
    package_data={
        setuptools.find_packages()[0]: [
            "dofast.json.zip", 'data/vps_init.sh', 'data/*.txt', 'data/*.conf',
            'pyavatar/templates/*.svg', 'pyavatar/templates/**/*.svg',
            'pyavatar/templates/**/**/*.svg'
        ]
    },
    install_requires=[
        'codefast==0.5.2dev3',
        'hashids',
        'colorlog>=4.6.1',
        'tqdm',
        'joblib',
        'PyGithub',
        'oss2',
        'lxml',
        'cos-python-sdk-v5',
        'smart-open',
        'pillow',
        'bs4',
        'arrow',
        'redis',
        'termcolor',
        'python-twitter',
        'python-telegram-bot',
        'deprecation',
        'faker',
        'pynsq',
        'flask',
        'googletrans==3.1.0a0',
        "cairosvg >= 2.3.0",
        'jinja2 >= 2.9.3',
    ],
    entry_points={
        'console_scripts': [
            'sli=dofast.sli_entry:main', 'hint=dofast.sli_entry:_hint_wubi',
            'snc=dofast.sli_entry:_sync', 'pxy=dofast.sli_entry:pxy',
            'websurf=dofast.nsq.websurf:run', 'weather=dofast.weather:entry',
            'jsy=dofast.sli_entry:jsonify',
            'tgpostman=dofast.nsq.telegram_postman:daemon',
            'qflask=dofast.qflask:run', 'sn=dofast.sli_entry:nsq_sync',
            'syncfile=dofast.nsq.syncfile:daemon', 'qget=dofast.qget:entry',
            'hemabot=dofast.sli_entry:hemabot', 'uu=dofast.ext.cli:app',
            'vps_monitor=dofast.linux.vps:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
