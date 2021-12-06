#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
No rights reserved. All files in this repository are released into the public
domain.
"""

from setuptools import setup

setup(
	# Some general metadata. By convention, a plugin is named:
	# opensesame-plugin-[plugin name]
	name='opensesame-plugin-RSVP',
	version='0.0.3',
	description='Add an RSVP task to an OpenSesame experiment',
	author='Robbert van der Mijn',
	author_email='robbertmijn@gmail.com',
	url='https://github.com/robbertmijn/opensesame-plugin-RSVP',
	# Classifiers used by PyPi if you upload the plugin there
	classifiers=[
		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering',
		'Environment :: MacOS X',
		'Environment :: Win32 (MS Windows)',
		'Environment :: X11 Applications',
		'License :: OSI Approved :: Apache Software License',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
	],
	# The important bit that specifies how the plugin files should be installed,
	# so that they are found by OpenSesame. This is a bit different from normal
	# Python modules, because an OpenSesame plugin is not a (normal) Python
	# module.
	data_files=[
		# First the target folder.
		('share/opensesame_plugins/RSVP_plugin',
		# Then a list of files that are copied into the target folder. Make sure
		# that these files are also included by MANIFEST.in!
		[
			'opensesame_plugins/RSVP_plugin/RSVP_plugin.md',
			'opensesame_plugins/RSVP_plugin/RSVP_plugin.png',
			'opensesame_plugins/RSVP_plugin/RSVP_plugin_large.png',
			'opensesame_plugins/RSVP_plugin/RSVP_plugin.py',
			'opensesame_plugins/RSVP_plugin/info.yaml',
			]
		)]
	)
