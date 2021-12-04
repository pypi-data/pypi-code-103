import setuptools

with open('README.md', 'r', encoding='utf-8') as fm:
    long_description = fm.read()

setuptools.setup(
    name='easygame',
    author_email='13513519246@139.com',
    author='stripe-python',
    maintainer='stripe-python',
    maintainer_email='13513519246@139.com',
    py_modules=setuptools.find_packages(),
    version='1.2.0',
    description='一个写游戏的框架,封装pygame',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=['pygame', 'pyperclip', 'playsound', 'pycaw', 'opencv-python'],
    python_requires='>=3.6',
)
