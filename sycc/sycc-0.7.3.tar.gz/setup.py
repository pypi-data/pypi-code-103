# 2020-2021
from setuptools import setup
import os
import platform
import sys, time
import sys
import threading
import subprocess

def pip_check_test():
	def pip_check_Exist():
		try:
		 	import pip
		except ImportError:
			return False
		else:
			return True
	if pip_check_Exist()==False:
		print('\033[1;1mpip不存在\033[0m')
	else:
		pass
	def pip_check_use():
		import os
		try:
			pip_check_use_global=str(os.popen('pip -V').read().splitlines(False)[0]).split(' ')[0]
			if 'pip' == pip_check_use_global:
				return True
			else:
				return False
		except:
			pass
	#print(pip_check_use())
	if (pip_check_use() and pip_check_Exist())==True:
		return 1


if platform.system() == "Linux":  #
    pass
elif platform.system() == "Windows":
    pass
elif pip_check_test()!=1:
	print('没有pip,不支持使用!')
	time.sleep(10)
	sys.exit()
else:
    print("不支持该系统")
    time.sleep(10)
    sys.exit()
try:
    import netifaces
except ImportError:
	#import os
	(
        threading.Thread(target=(subprocess.call("pip install netifaces", shell=True)))
    ).start()    

  
__Author__ = "神秘的·"
__project_start_time__ = "2020"
__date_end_time__ = "2021/11"
HERE = os.path.abspath(os.path.dirname(__file__))
print("\n\n| " + "PATH::README.rst:", HERE + " |\n\n")
with open(os.path.join(HERE, "README.rst")) as rst:
    R = rst.read()
setup(
    name="sycc",  # sycc
    py_modules=["sycc", "core", "__init__", "v"],
    version="0.7.3",
    description="虹源三式(四圆计算器)",  # 原
    long_description=R,
    classifiers=[
        "Natural Language :: Chinese (Simplified)",
        "Development Status :: 6 - Mature",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Android",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Terminals",
        "Topic :: System :: Shells",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
    ],
    keywords=[
        "sycc",
        "3y",
        "a_3y",
        "Circle",
        "圆",
        "圆柱",
        "圆环",
        "py",
        "Chinese",
        "ycc",
        "python",
        "windows",
        "linux",
        "3",
        "y",
        "yh",
        "yz",
        "qt",
        "4",
        "4y",
        "计算器",
        "Calculator",
        "edu",
    ],  # 关键字
    author=__Author__,
    author_email="lwb29@qq.com",
    url="https://github.com/py-lwb/sycc",
    license="sycc license",
    packages=["p", "k", "e", "colorama", "p/tqdm","pip_check"],
    python_requires=">=3.6",
    install_requires=["netifaces>=0.11.0", "sycc>=0.6.0"],
    entry_points={
        "console_scripts": [
            "sycc = sycc:main",
        ]
    },
    project_urls={
        "github": "https://github.com/py-lwb/sycc",
        "pypi": "https://pypi.org/project/sycc/",
    },
    include_package_data=True,
    zip_safe=True,
)
if os.path.exists("setup.cfg") == True:
    os.remove("setup.cfg")
