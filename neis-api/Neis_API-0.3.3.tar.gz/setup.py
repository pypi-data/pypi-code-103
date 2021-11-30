import setuptools

setuptools.setup(
    name="Neis_API",
    version="0.3.3",
    license='MIT',
    author="PIO",
    author_email="seungyounyou0220@gmail.com",
    description="나이스 API를 활용할 수 있게 도와주는 파이썬 패키지 입니다",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Piop2/Neis_API",
    packages=setuptools.find_packages(),
    classifiers=[
        # 패키지에 대한 태그
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)
