from distutils.core import setup
setup(
name='baizhancmbStudy', # 对外我们模块的名字
version='1.0', # 版本号
description='这是第一个对外发布的模块，里面有数学方法测试哦', #描述
author='chenmingbo', # 作者陈
author_email='371175848@qq.com',
py_modules=['baizhancmbStudy.demo1','baizhancmbStudy.demo2'] # 要发布的模块
)