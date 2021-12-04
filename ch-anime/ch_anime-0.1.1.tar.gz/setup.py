import setuptools
with open("idk", "r") as lo:
    long_description = lo.read()

setuptools.setup(
     name='ch_anime',  
     version='0.1.1',
     author="phillychi3",
     author_email="phillychi3@gmail.com",
     description="some spider",
     long_description=long_description,
     url="https://github.com/phillychi3/ch_anime",
     py_modules=["spider","web crawler","webcrawler","anime"],
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: Apache Software License",
         "Operating System :: OS Independent",
     ]
    
 )