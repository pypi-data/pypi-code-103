#! /usr/bin/env python3

import os
import sys
import json
import faker
import argparse
import subprocess
import logging
import requests 
from telegraph.api import Telegraph
from telegraph.utils import html_to_nodes
from icecream import ic

__author__="Muhammad Al Fajri"
__email__="fajrim228@gmail.com"
__telegram__="https://t.me/ini_peninggi_badan"

# logging.basicConfig(level=logging.DEBUG)
def create_page(path, values: dict = None):
	"""
	Simple!
	"""
	try:
		r = requests.post(f'https://api.telegra.ph/{path}', params=values)
		return r.json()
	except Exception as e:
		raise e
	
def get_all_page():
	'''
	Place a description
	'''
	T = Telegraph(access_token = token)
	response = T.get_page_list()
	return response

def create_token(author: str, short_name: str):
	'''
	Place a description
	'''
	data = {
		'short_name':short_name,
		'author_name':author
	}
	r = requests.post('https://api.telegra.ph/createAccount', params=data)
	return r.json()
	
def main(
		string_input: str = None,
		args_filename: str = None,
		args_author: str = None,
		args_author_url: str = None,
		args_page: str = None,
		args_title: str = 'Couldn\'t find any title'
	):
	global __author__
	name = faker.Faker().name()
	short_name = name.split()[0]
	token = create_token(name, short_name)['result']['access_token']
	author_name = __author__
	author_url = "https://t.me/" + __telegram__
	'''
	* this is the main script, you only need to call this one.
	* take an argument (text/html) for now, default to None

	'''
	if args_page:
		print(get_all_page())
		sys.exit(0)
	if args_filename:
		html_file = args_filename
	elif not args_filename:
		ic()
		try:	
			html_file = os.getenv('HTML_FILE')
		except:
			return None
	if args_title:
		title = args_title
	else:
		ic()
		try:
			title = html_file.replace('-', ' ')
		except:
			title = 'No Title'
	if args_author:
		author_name = args_author
	else:
		author_name = author_name
	if args_author_url:
		author_url = args_author_url
	else:
		author_url = author_url
	if html_file:
		a = open(html_file).read()
		content = html_to_node(a)
	else:
		if string_input:
			content = html_to_nodes(string_input)
		else:
			return None
	content_json = json.dumps(content, ensure_ascii=False)
	data = {
		'access_token':token,
		'title': title,
		'author_name': author_name,
		'author_url': author_url,
		'content': content_json,
		'return_content': True
	}
	try:
		endpoint = title.replace(' ', '---').lower()
		url =  (
			create_page('createPage', data)['result']['url']
		)
		new_url = requests.post('http://ik-a.herokuapp.com/custom', json={'id':endpoint, 'url':url}).json()['url']
		return new_url
		
	except Exception as e:
		return None
