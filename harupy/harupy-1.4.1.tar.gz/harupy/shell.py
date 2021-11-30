#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import getpass


def root_only(func):
	"""
	루트 유져만 실행할 수 있게 제한하는 데코레이터
	"""
	def inner(*args, **kwargs):
		if os.getuid() is 0:
			return func(*args, **kwargs)
		else:
			print("root 유져만 실행 가능합니다.")
			return False

	return inner


def cmd(command):
	"""
	쉘 명령 수행 후 Standard Output과 Standard Error를 리턴
	:return: (bytes, bytes)
	"""
	popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	(stdoutdata, stderrdata) = popen.communicate()
	return stdoutdata, stderrdata


def confirm(output, default=None):
	"""
	진행될 내용을 표시하고 유져에게 확인 받기
	:return: Boolean
	"""
	suffix = ('[y/N]', '[Y/n]', '[Y/N]')
	default = 1 if default is True else 0 if default is False else 2
	while True:
		print(output, end=' ')
		i = input(suffix[default]).strip().lower()
		if len(i) == 0:
			if default == 2:
				continue
			else:
				return True if default else False
		if i in ('y', 'yes'):
			return True
		elif i in ('n', 'no'):
			return False


def password(prompt="비밀번호 : ", reprompt="비밀번호 확인 : ", min_length=6):
	"""
	비밀번호 2회 입력으로 확인하면서 입력 받기
	:return: str
	"""
	while True:
		while True:
			pw = getpass.getpass(prompt)
			if min_length <= len(pw):
				break
			else:
				print("길이가 최소 %d자 이상 되어야 합니다." % min_length)
		if not reprompt:
			break
		if getpass.getpass(reprompt) == pw:
			break
		else:
			print("일치하지 않습니다. 다시 입력해주세요.")
	return pw
