from setuptools import setup, find_packages
setup(
    name="twintowers",
    version="0.2.3",
    author="LTEnjoy",
    author_email="sujinltenjoy@gmail.com",
    description="protein homology detection using deep learning",
    install_requires=['faiss'],
    include_package_data=True,
    
    # 你要安装的包，通过 setuptools.find_packages 找到当前目录下有哪些包
    packages=find_packages(),
    
    entry_points={
        'console_scripts': [
            'twintowers = TwinTowers.command:tasks'
        ]
    }
)
