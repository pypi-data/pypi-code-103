import os
from setuptools import find_packages, setup
from shutil import copyfile




def readme():
    with open('README.rst') as f:
        return f.read()


os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
# The full version, including alpha/beta/rc tags.
release = os.popen('git tag').read().strip()
# The short X.Y version.

branch =os.popen("git branch | grep \* | cut -d ' ' -f2 ").read().strip()
version = "0.1"
global_version = False
try :
        f = open("dist_V"+version+".txt", "r")
        prev_build= f.read()

except:
        prev_build= 0
        global_version = True

if global_version :
    try :
        f = open("dist_Glob_V" + version + ".txt", "r")
        prev_build = f.read()
        global_version = True
    except :
        prev_build = 0
        global_version = False
print('previous build '+str(prev_build))
if global_version :
    new_build = prev_build
else :
    new_build= int(prev_build)+1

newName='bailamapi'
newVersion=version+str(new_build)

print(f"new version is {newVersion}")
setup(name=newName,
      version=newVersion,
      description='Python APi form Bailam:'+branch,
      author='Olivier Kamoun',
      author_email='okamoun@bailam.com',
      license='Copyright Bailam',
      packages=['bailamapi'],
      package_data={'': ['*.html','*.json', '*.tpl'] ,'field_tagger':['*.pkl'],'dictionaries': ['data/*.json'] },
      include_package_data=True,
      zip_safe=False, install_requires=['pandas','requests','xlrd','openpyxl'],
      )


try :


    if not (global_version):

        text_file = open("dist_V"+version+".txt", "w")

        text_file.write(str(new_build))

        text_file.close()


        text_file = open("dist_Glob_V" + version + ".txt", "w")

        text_file.write(str(new_build))

        text_file.close()

except :
        print('could not update sequence ')