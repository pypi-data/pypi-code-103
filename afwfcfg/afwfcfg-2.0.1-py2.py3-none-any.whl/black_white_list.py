#!/usr/bin/env python
# coding=utf-8

from ctypes import *
from afwfcfg.afwf_log import *

so_path = r'/usr/lib/liburlmatch.so'
licence_path = r'/opt/afwf/licenses/licence.conf'

try:
    lib_match = cdll.LoadLibrary(so_path)
except OSError:
    lib_match = cdll.LoadLibrary("/Users/dongze/works/coding/anti_fraud")
except Exception as e:
    print(f"未发现so文件：{so_path}: {e}")
    lib_match = None

# url类型
URL_TYPE_GRAY = 1
URL_TYPE_BLACK = 2
URL_TYPE_WHITE_NO_QQ = 3
URL_TYPE_WHITE_QQ = 4

# url级别
# mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507
URL_LEVEL_URL = 1
# mail.qq.com/cgi-bin/frame_html
URL_LEVEL_CGI = 2
# mail.qq.com/cgi-bin
URL_LEVEL_PATH = 3
# mail.qq.com
URL_LEVEL_HOST = 4
# qq.com
URL_LEVEL_DOMAIN = 5

# url级别字典
leveldict = {
    'url': URL_LEVEL_URL,
    'cgi': URL_LEVEL_CGI,
    'path': URL_LEVEL_PATH,
    'host': URL_LEVEL_HOST,
    'domain': URL_LEVEL_DOMAIN
}


"""
    功能描述: 黑白名单模块初始化接口
    参数: 无
    返回值: -1: 腾讯库初始化失败
        -2: 自定义库初始化失败
         0: 初始化成功
    说明: 在使用黑白名单添加功能时，需要先调用初始化接口，同一进程中只需要在进程初始化时调用一次。
"""


def BlackWhiteInit():
    return lib_match.match_init(licence_path)


"""
    功能描述: 黑白名单模块添加url条目
    参数:    url,     url字符串
            level,   leveldict中的一种
            urltype, url类型(1-4)
    返回值:  0x00: 添加成功
            0x31: 错误的url
            0x32: 错误的url级别
            0x33: 错误的url类别
    说明: 黑白名单调用clib添加到共享内存
"""


def AddUrl(url, level, urltype):
    return lib_match.add_url(url, level, urltype)


"""
    功能描述: 黑白名单模块删除url条目
    参数: url,   url字符串
        level, leveldict中的一种
    返回值:  0x00: 删除成功
            0x41: url参数无效
            0x42: level参数无效
            0x43: 删除失败, 指定的条目不存在
    说明: 黑白名单调用clib从共享内存删除
"""


def DelUrl(url, level):
    return lib_match.del_url(url, level)


"""
    功能描述: 添加单条白名单url条目
    参数: url,  url字符串
    返回值: 0x00: 添加成功
        0x31: 错误的url
    说明: 此接口添加的白名单仅对url该生效，即level级别为1
"""


def WHITE_URL_Add(url):
    ret = AddUrl(url, URL_LEVEL_URL, URL_TYPE_WHITE_NO_QQ)
    AFWF_Info('add white url %s ret %s' % (url, hex(ret)))
    return ret


"""
    功能描述: 删除单条白名单url条目
    参数: url,   url字符串
    返回值: 0x00: 删除成功
        0x41: url参数无效
        0x42: level参数无效
        0x43: 删除失败, 指定的条目不存在
    说明: 此接口仅删除level级别为1的url条目
"""


def WHITE_URL_Del(url):
    ret = DelUrl(url, URL_LEVEL_URL)
    AFWF_Info('del white url %s ret %s' % (url, hex(ret)))
    return ret


"""
    功能描述: 添加指定url级别的白名单url条目
    参数: url,   url字符串
        level, leveldict中的一种(1-5)
    返回值: 0x00: 添加成功
        0x31: 错误的url
        0x32: 错误的url级别
    说明: 无
"""


def WHITE_URL_AddWithLevel(url, level):
    ret = AddUrl(url, level, URL_TYPE_WHITE_NO_QQ)
    AFWF_Info('add white level %u url %s ret %s' % (level, url, hex(ret)))
    return ret


"""
    功能描述: 删除指定url级别的白名单url条目
    参数: url,   url字符串
        level, leveldict中的一种(1-5)
    返回值: 0x00: 删除成功
        0x41: url参数无效
        0x42: level参数无效
        0x43: 删除失败, 指定的条目不存在
    说明: 无
"""


def WHITE_URL_DelWithLevel(url, level):
    ret = DelUrl(url, level)
    AFWF_Info('del white level %u url %s ret %s' % (level, url, hex(ret)))
    return ret


"""
    功能描述: 添加单条黑名单url条目
    参数: url,   url字符串
    返回值:  0x00: 添加成功
            0x31: 错误的url
    说明: 此接口添加的黑名单仅对url该生效，即level级别为1
"""


def BLACK_URL_Add(url):
    ret = AddUrl(url, URL_LEVEL_URL, URL_TYPE_BLACK)
    AFWF_Info('add black url %s ret %s' % (url, hex(ret)))
    return ret


"""
    功能描述: 删除单条黑名单url条目
    参数: url,   url字符串
    返回值: 0x00: 删除成功
        0x41: url参数无效
        0x42: level参数无效
        0x43: 删除失败, 指定的条目不存在
    说明: 此接口仅删除level级别为1的url条目
"""


def BLACK_URL_Del(url):
    ret = DelUrl(url, URL_LEVEL_URL)
    AFWF_Info('del black url %s ret %s' % (url, hex(ret)))
    return ret


"""
    功能描述: 添加指定url级别的黑名单url条目
    参数: url,   url字符串
        level, leveldict中的一种(1-5)
    返回值: 0x00: 添加成功
        0x31: 错误的url
        0x32: 错误的url级别
    说明: 无
"""


def BLACK_URL_AddWithLevel(url, level):
    ret = AddUrl(url, level, URL_TYPE_BLACK)
    AFWF_Info('add black level %u url %s ret %s' % (level, url, hex(ret)))
    return ret


"""
    功能描述: 删除指定url级别的黑名单url条目
    参数: url,   url字符串
        level, leveldict中的一种(1-5)
    返回值: 0x00: 删除成功
        0x41: url参数无效
        0x42: level参数无效
        0x43: 删除失败, 指定的条目不存在
    说明: 无
"""


def BLACK_URL_DelWithLevel(url, level):
    ret = DelUrl(url, level)
    AFWF_Info('del black level %u url %s ret %s' % (level, url, hex(ret)))
    return ret


"""
    功能描述: url匹配接口
    参数: url,   url字符串
    返回值:
    说明: 此接口只做测试用，暂不对外提供
"""


def m_match(url):
    urltype = c_int(4)
    purltype = pointer(urltype)
    eviltype = c_int(4)
    peviltype = pointer(eviltype)
    domaintype = c_int(4)
    pdomaintype = pointer(domaintype)

    url = url.encode('utf-8')
    ret = lib_match.match_murl_web(url, len(url), purltype, peviltype, pdomaintype)
    return hex(ret), urltype.value, eviltype.value, domaintype.value


if __name__ == '__main__':
    mh = lib_match.match_init('/opt/afwf/licenses/licence.conf')
    print('licence check:', mh)
    
    print('white del:', hex(WHITE_URL_Del('www.baidu.com')))
    print('white add:', hex(WHITE_URL_Add('https://www.baidu.com')))
    print('white del:', hex(WHITE_URL_Del('www.baidu.com')))
    print('url match:', m_match('https://www.baidu.com'))
    print('white add:', hex(WHITE_URL_Add('https://www.baidu.com')))
    print('url match:', m_match('https://www.baidu.com'))
    print('url match:', m_match('http://www.baidu.com'))
    print('url match:', m_match('www.baidu.com'))
    print('black del:', hex(BLACK_URL_Del('https://www.baidu.com')))
     
    print('\r\n')
    print('black del:', hex(WHITE_URL_Del('www.baidu.com')))
    print('black add:', hex(BLACK_URL_Add('https://www.baidu.com')))
    print('black del:', hex(WHITE_URL_Del('www.baidu.com')))
    print('url match:', m_match('https://www.baidu.com'))
    print('black add:', hex(BLACK_URL_Add('www.baidu.com')))
    print('url match:', m_match('https://www.baidu.com'))
    print('url match:', m_match('http://www.baidu.com'))
    print('url match:', m_match('www.baidu.com'))
    print('black del:', hex(BLACK_URL_Del('https://www.baidu.com')))
    
    '''print 'white del:', hex(WHITE_URL_Del('www.baidu.com'))
    print 'white del:', hex(WHITE_URL_Del('www.baidu.com'))
    print 'url match:', m_match('abc.com/abcd/1235.html')
    #print 'white add:', hex(WHITE_URL_Add('www.baidu.com'))
    #print 'black add:', hex(BLACK_URL_Add('www.baidu.com'))
    print 'white add:', hex(WHITE_URL_AddWithLevel('www.baidu.com/abc', 4))
    print 'url match:', m_match('baidu.com')
    print 'white add:', hex(WHITE_URL_AddWithLevel('www.500pe.com/cfg.html', 4))
    print 'white del:', hex(WHITE_URL_Del('www.500pe.com/cfg.html'))
    print 'white add:', hex(BLACK_URL_AddWithLevel('www.500pe.com/cfg.html', 4))
    print 'white add:', hex(WHITE_URL_AddWithLevel('www.500pe.com/cfg.html', 4))
    print 'white del:', hex(WHITE_URL_Del('www.500pe.com'))
    print 'white del:', hex(BLACK_URL_Del('www.500pe.com'))
    print 'url match:', m_match('www.500pe.com/cfg.html')

    print 'white del:', hex(BLACK_URL_Del('qq.com'))
    print 'white add:', hex(BLACK_URL_AddWithLevel('mail.qq.com', 4))
    #print 'white add:', hex(BLACK_URL_AddWithLevel('qq.com', 1))
    print 'url match:', m_match('qq.com')
    print 'white del:', hex(BLACK_URL_Del('mail.qq.com'))
    print 'url match:', m_match('mail.qq.com')'''
    '''for i in range(0, 100):
        print 'black add:', hex(BLACK_URL_AddWithLevel('www.abcd.com/test_%d.html'%i, 3))
        print 'url match:', m_match('www.abcd.com/test_%d.html'%i)
        print 'www.abcd.com/test_%d.html'%i
        print 'black del:', hex(BLACK_URL_Del('www.abcd.com/test_%d.html'%i))'''
    print('-------------------------------5-------------------------')
    print('black add:', hex(BLACK_URL_AddWithLevel('qq.com', 5)))
    print('url match:', m_match('qq.com'))
    print('url match:', m_match('mail.qq.com'))
    print('url match:', m_match('mail.qq.com/cgi-bin'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507'))
    print('black del:', hex(BLACK_URL_DelWithLevel('qq.com', 5)))
    print('url match:', m_match('qq.com'))

    print('white add:', hex(WHITE_URL_AddWithLevel('qq.com', 5)))
    print('url match:', m_match('qq.com'))
    print('url match:', m_match('mail.qq.com'))
    print('url match:', m_match('mail.qq.com/cgi-bin'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507'))
    print('white del:', hex(WHITE_URL_DelWithLevel('qq.com', 5)))
    print('url match:', m_match('qq.com'))

    print('-------------------------------4-------------------------')
    print('black add:', hex(BLACK_URL_AddWithLevel('qq.com', 4)))
    print('url match:', m_match('qq.com'))
    print('url match:', m_match('mail.qq.com'))
    print('url match:', m_match('mail.qq.com/cgi-bin'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507'))
    print('black del:', hex(BLACK_URL_DelWithLevel('qq.com', 4)))
    print('url match:', m_match('qq.com'))

    print('white add:', hex(WHITE_URL_AddWithLevel('qq.com', 4)))
    print('url match:', m_match('qq.com'))
    print('url match:', m_match('mail.qq.com'))
    print('url match:', m_match('mail.qq.com/cgi-bin'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507'))
    print('white del:', hex(WHITE_URL_DelWithLevel('qq.com', 4)))
    print('url match:', m_match('qq.com'))

    print('-------------------------------4-------------------------')
    print('black add:', hex(BLACK_URL_AddWithLevel('mail.qq.com', 4)))
    print('url match:', m_match('qq.com'))
    print('url match:', m_match('mail.qq.com'))
    print('url match:', m_match('mail.qq.com/cgi-bin'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507'))
    print('black del:', hex(BLACK_URL_DelWithLevel('mail.qq.com', 4)))
    print('url match:', m_match('mail.qq.com'))

    print('white add:', hex(WHITE_URL_AddWithLevel('mail.qq.com', 4)))
    print('url match:', m_match('qq.com'))
    print('url match:', m_match('mail.qq.com'))
    print('url match:', m_match('mail.qq.com/cgi-bin'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507'))
    print('white del:', hex(WHITE_URL_DelWithLevel('mail.qq.com', 4)))
    print('url match:', m_match('mail.qq.com'))

    print('-------------------------------3-------------------------')
    print('black add:', hex(BLACK_URL_AddWithLevel('mail.qq.com/cgi-bin', 3)))
    print('url match:', m_match('qq.com'))
    print('url match:', m_match('mail.qq.com'))
    print('url match:', m_match('mail.qq.com/cgi-bin'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507'))
    print('black del:', hex(BLACK_URL_DelWithLevel('mail.qq.com/cgi-bin', 3)))
    print('url match:', m_match('mail.qq.com/cgi-bin'))

    print('white add:', hex(WHITE_URL_AddWithLevel('mail.qq.com/cgi-bin', 3)))
    print('url match:', m_match('qq.com'))
    print('url match:', m_match('mail.qq.com'))
    print('url match:', m_match('mail.qq.com/cgi-bin'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507'))
    print('white del:', hex(WHITE_URL_DelWithLevel('mail.qq.com/cgi-bin', 3)))
    print('url match:', m_match('mail.qq.com/cgi-bin'))

    print('-------------------------------2-------------------------')
    print('black add:', hex(BLACK_URL_AddWithLevel('mail.qq.com/cgi-bin/frame_html', 2)))
    print('url match:', m_match('qq.com'))
    print('url match:', m_match('mail.qq.com'))
    print('url match:', m_match('mail.qq.com/cgi-bin'))
    print('rl match:', m_match('mail.qq.com/cgi-bin/frame_html'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507'))
    print('black del:', hex(BLACK_URL_DelWithLevel('mail.qq.com/cgi-bin/frame_html', 2)))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html'))

    print('white add:', hex(WHITE_URL_AddWithLevel('mail.qq.com/cgi-bin/frame_html', 2)))
    print('url match:', m_match('qq.com'))
    print('url match:', m_match('mail.qq.com'))
    print('url match:', m_match('mail.qq.com/cgi-bin'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507'))
    print('white del:', hex(WHITE_URL_DelWithLevel('mail.qq.com/cgi-bin/frame_html', 2)))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html'))

    print('-------------------------------1-------------------------')
    print('black add:', hex(BLACK_URL_AddWithLevel('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507', 1)))
    print('url match:', m_match('qq.com'))
    print('url match:', m_match('mail.qq.com'))
    print('url match:', m_match('mail.qq.com/cgi-bin'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507'))
    print('black del:', hex(BLACK_URL_DelWithLevel('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507', 1)))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507'))

    print('white add:', hex(WHITE_URL_AddWithLevel('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507', 1)))
    print('url match:', m_match('qq.com'))
    print('url match:', m_match('mail.qq.com'))
    print('url match:', m_match('mail.qq.com/cgi-bin'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html'))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507'))
    print('white del:', hex(WHITE_URL_DelWithLevel('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507', 1)))
    print('url match:', m_match('mail.qq.com/cgi-bin/frame_html?sid=Uch_hMabTYPCAT1q&r=354da9218e017a8b87a272529853a507'))
