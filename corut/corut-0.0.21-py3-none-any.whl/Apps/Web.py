#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
It is aimed to develop functions that will process the data received over the web.
It is intended to produce solutions that manage post/request events on any target site.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

import requests
from webbrowser import open as _url_open
from bs4 import BeautifulSoup
from ..Decorators import try_except


@try_except
def connect_with_request(url, user, password, proxies=None, **kwargs):
    session = requests.Session()
    if proxies:
        session.proxies = proxies
    response = session.get(url, auth=(user, password), **kwargs)
    print(f'Status: {response.status_code} ---> URL:{url}')
    return session, response


@try_except
def download_file_from_google_drive(google_drive_id, target_path, proxies=None):
    def get_confirm_token(_response):
        for key, value in _response.cookies.items():
            if key.startswith('download_warning'):
                return value
        return None

    url = "https://drive.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(url, params={'id': google_drive_id}, proxies=proxies, stream=True)
    token = get_confirm_token(response)
    if token:
        params = {'id': google_drive_id, 'confirm': token}
        response = session.get(url, params=params, proxies=proxies, stream=True)
    download_file_from_url(target_path=target_path, response=response)


@try_except
def download_file_from_url(target_path, url=None, response=None, proxies=None):
    if url and response is None:
        print(f'Downloading file at link {url}')
        response = requests.get(url, stream=True, proxies=proxies)
    with open(target_path, "wb") as f:
        for part, chunk in enumerate(response.iter_content(1024 * 1024)):
            if chunk:
                f.write(chunk)
                print(f'{part} MB Download Successful.')
    print(f'File Download successful...:{target_path}')


@try_except
def fetch_all_data_in_table(table, separator="", strip=False):
    """
    It is intended to parse the HTML data received with the request.
    HTML data is converted to table and parsed in column and row format.
    :param table: data to be parsed. for example; table = BeautifulSoup(html, "html.parser")
    :param separator: string information parser in rows
    :param strip: If you want to pass empty data
    :return: Returns data in tabular format
    """
    rows = []
    tr_all = table.find_all('tr')
    head_line = [td.get_text(separator=separator, strip=strip) for td in tr_all[0].find_all('th')]
    if head_line:
        rows.append(head_line)
        tr_all = tr_all[1:]
    for tr in tr_all:
        rows.append([td.get_text(separator=separator, strip=strip) for td in tr.find_all('td')])
    return rows


@try_except
def get_bs4(
        markup="", features=None, builder=None, parse_only=None,
        from_encoding=None, exclude_encodings=None, element_classes=None, **kwargs
):
    """
    For the document, you should look at the documents in the BeautifulSoup class from bs4.
    :param markup:
    :param features:
    :param builder:
    :param parse_only:
    :param from_encoding:
    :param exclude_encodings:
    :param element_classes:
    :param kwargs:
    :return:
    """
    return BeautifulSoup(
        markup=markup, features=features, builder=builder, parse_only=parse_only,
        from_encoding=from_encoding, exclude_encodings=exclude_encodings,
        element_classes=element_classes,
        **kwargs
    )


@try_except
def open_link_on_browser(url, new_tab=True, auto_raise=True):
    """
    Opens any link in the browser
    :param url: Opens single or multiple urls
    :param new_tab: Open in an existing browser or open in a new browser
    :param auto_raise: return open state
    """
    situations = []
    for u in [url] if isinstance(url, str) else url:
        situations.append(_url_open(url=u, new=2 if new_tab else 1, autoraise=auto_raise))
    return situations[0] if len(situations) == 1 else situations


@try_except
def read_url(
        connection, url, parser="html.parser",
        find="table", max_line_on_page=None, next_page_url=None
):
    def get_data(_url):
        print(f'Read URL : {_url}')
        response = connection.get(_url)
        response = response.text
        table = get_bs4(response, parser).find(find)
        if table is None:
            return None
        return fetch_all_data_in_table(table, separator='\t', strip=True)

    if max_line_on_page and next_page_url:
        _data = []
        _nex_page = 1
        while True:
            values = None
            for repeat in range(4):
                values = get_data(f"{url}{next_page_url}{_nex_page}")
                if values:
                    break
            if values:
                _data.extend(values)
            if len(values) < max_line_on_page:
                break
            _nex_page += 1
        return _data
    else:
        return get_data(url)
