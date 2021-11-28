# -*- coding: utf-8 -*-
import pytest
from bs4 import BeautifulSoup
from zwutils import htmlutils
from zwutils import fileutils

def test_find_soup_parent():
    htmlstr = '''
    <table class="myclass otherclass">
    <thead></thead>
    <tbody>
        <tr><td id="a"></td></tr>
        <tr></tr>
    </tbody>
    </table>
    '''
    el = BeautifulSoup(htmlstr, features='lxml')
    el = el.find(id='a')
    r = htmlutils.find_soup_parent(el, tagnm='table')
    assert r and r.name == 'table'

    r = htmlutils.find_soup_parent(el, attrs={'class': 'myclass'})
    assert r and r.name == 'table'

    r = htmlutils.find_soup_parent(el, tagnm='table', attrs={'class': 'myclass'})
    assert r and r.name == 'table'

def test_find_soup_next_sibling():
    htmlstr = '''
    <table>
    <thead></thead>
    <tbody>
        <tr><td id="a">label</td><td>text1</td><td class="myclass otherclass">text2</td></tr>
        <tr></tr>
    </tbody>
    </table>
    '''
    el = BeautifulSoup(htmlstr, features='lxml')
    el = el.find(id='a')
    r = htmlutils.find_soup_next_sibling(el, tagnm='td')
    assert r and r.text == 'text1'

    r = htmlutils.find_soup_next_sibling(el, attrs={'class': 'myclass'})
    assert r and r.text == 'text2'

    r = htmlutils.find_soup_next_sibling(el, tagnm='td', attrs={'class': 'myclass'})
    assert r and r.text == 'text2'

def test_soup_depth_count():
    htmlstr = '''
    <table>
    <thead></thead>
    <tbody>
        <tr id="tr"><td id="td">label</td></tr>
        <tr></tr>
    </tbody>
    </table>
    '''
    soup = BeautifulSoup(htmlstr, features='lxml')
    el = soup.find(id='td')
    r = htmlutils.soup_depth_count(el)
    assert r == 3

    soup = BeautifulSoup(htmlstr, features='lxml')
    el = soup.find(id='tr')
    r = htmlutils.soup_depth_count(el, 'html')
    assert r == 3

def test_soup_calc_child():
    htmlstr = '''
    <table>
    <thead></thead>
    <tbody>
        <tr id="tr"><td id="td">label</td><td></td></tr>
        <tr></tr>
    </tbody>
    </table>
    '''
    soup = BeautifulSoup(htmlstr, features='lxml')
    r = htmlutils.soup_calc_child(soup, 'td')
    assert r[2]['child_count'] == 2 and r[2]['depth_count'] == 2

def test_soup_calc_word():
    htmlstr = '''
    <html>
    <head>HAHA</head>
    <body>
        <table>
            <thead></thead>
            <tbody>
                <tr><td>这是标题，不是主体</td></tr>
                <tr></tr>
            </tbody>
        </table>
        <table>
            <thead>这是header，也不是主体</thead>
            <tbody>
                <tr><td>这是主体了</td></tr>
                <tr><td>厅机关各处室，中心、所：</td></tr>
                <tr><td>根据军队转业干部接收安置有关政策，经厅党组研究决定，确定姜学明同志为四级调研员。</td></tr>
                <tr><td>中共江苏省商务厅党组</td></tr>
                <tr><td>2020年2月13日</td></tr>
                <tr><td>这是主体了</td></tr>
                <tr></tr>
            </tbody>
        </table>
        <div>这仍然不是主体</div>
    </body>
    </html>
    '''
    soup = BeautifulSoup(htmlstr, features='lxml')
    r = htmlutils.soup_calc_word(soup)
    arr = sorted(r, key=lambda o: o['gscore'], reverse=True)
    assert 1

def test_soup_drop_tag():
    htmlstr = '''
    <div>
        <p>abc</p>
        456
        <em>
            def
            <p>789</p>
            <p>ghi</p>
        </em>
        <p>xxx</p>
        zzz
    </div>
    '''
    soup = BeautifulSoup(htmlstr, features='lxml')
    # fileutils.writefile('bef.html', str(soup))
    htmlutils.soup_drop_tag(soup.find('em'))
    # fileutils.writefile('aft.html', str(soup))
    assert 1
