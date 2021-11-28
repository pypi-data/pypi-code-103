# -*- coding: utf-8 -*-
import pytest

from zwutils import reutils

@pytest.mark.parametrize(
    'input, result', (
        ('\n118.113.245.40\n8167\n高匿\nhttp\n中国\n四川省成都市\n电信\n1.379 秒\n6分钟前\n\n', '118.113.245.40'),
        ('\n118.113.245.40:9999\n8167\n高匿\nhttp\n中国\n四川省成都市\n电信\n1.379 秒\n6分钟前\n\n', '118.113.245.40:9999'),
        ('aaa118.113.245.40:9999asdfadf118.113.245.40:9999safadfaf118.113.245.40', '118.113.245.40:9999'),
    )
)
def test_find_ip(input, result):
    r = reutils.find_ip(input)
    assert r[0] == result

@pytest.mark.parametrize(
    'input, result', (
        ('\n118.113.245.40\n8167\n高匿\nhttp\n中国\n四川省成都市\n电信\n1.379 秒\n6分钟前\n\n', 8167),
    )
)
def test_find_port(input, result):
    r = reutils.find_port(input)
    assert r[0] == result

@pytest.mark.parametrize(
    'input, result', (
        ('http://wb.jiangsu.gov.cn   http://www.jsfao.gov.cn', 2),
        ('http://www.jiangsu.gov.cn；http://www.js.gov.cn', 2),
    )
)
def test_urls_from_str(input, result):
    r = reutils.urls_from_str(input)
    assert len(r) == result

@pytest.mark.parametrize(
    's, arr, result', (
        ('\n\n索引号\n文号', ('索引号', '文号'), True),
        ('\n\n索引号 名称\n文号\n生成日期\n', ('索引号', '文号'), True),
        ('\n\n索引号 名称\n文号\n生成日期\n', ['索引号', '文号'], True),
        ('\n\n索引号 名称\n文号\n生成日期\n', ['索引号', '编号'], False),
    )
)
def test_multi_match(s, arr, result):
    r = reutils.multi_match(s, arr)
    assert r == result

def test_htmltag_by_name():
    htmlstr = '''
    <div>
        <iframe name="subinfo" width="100%" height="530" id="subinfo" src="/module/xxgk/subjectinfo.jsp?area=014000335" frameborder="0"></iframe>
    </div>
    '''
    r = reutils.htmltag_by_name(htmlstr, 'iframe')
    a = 0