#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import ConfigParser
import os
import codecs
import sys
from log import logger

#修复key全转为小写问题
class MyConfigParser(ConfigParser.SafeConfigParser):
    def __init__(self, defaults=None):
        ConfigParser.SafeConfigParser.__init__(self, defaults=defaults)
    def optionxform(self, optionstr):
        return optionstr

def read_conf(conf_file):
    if not os.path.exists(conf_file):
       raise Exception("not exists config file :%s"%(conf_file))
    else:
    #文件不存在也不处理 让调用者自己决定怎么处理该异常
        #读出来的是 unicode 编码 推荐 ,
        #config = ConfigParser.SafeConfigParser()
        config=MyConfigParser()
        with codecs.open(conf_file, 'r', encoding='utf-8') as f:
            config.readfp(f)
        return config

def main(conf_file=''):
    #没传配置文件时, 需要传环境参数 prod|dev|test 等用于对应的配置文件
    if conf_file=='':
        try:
            env=sys.argv[1]
        except BaseException as e:
            raise Exception("paramsError: usage : python main.py env  [other params ] , env use for conf file , like prod|dev|test")
        #默认取项目路径下 conf/conf_xxx 配置文件
        conf_file =os.path.join(os.getcwd(),'conf','conf_%s.cfg'%sys.argv[1])
    config=read_conf(conf_file)
    return(config)

if __name__ == '__main__':
    config=main()
    # 获取各个section 下的 所有的配置项名
    print(config.has_section('sdf'))
    for section in config.sections():
        print(config.options(section))
    for options in config.options(section):  # 获取所有 key
        print options  # key
        print(config.get(section, options))  # val
    for item in config.items(section):  # (key,val)
        print item


