#!/bin/python3
# (c) Sebastian GABRIEL <dev@3134.at>

"""
GitAutoVersion generates a descriptive versionstring in git repositories automatically using git-describe.
"""
import sys
import os
import re
from git import Repo


def getVersionString(
	git_repo:Repo,
	flag_development:str = "DEVELOPMENT",
	flag_git:str = "git",
	flag_branch:str = "branch",
	flag_dirty:str = "DIRTY",
	version_prefix:str = "v" ):
	'''
	Takes git repo and converts git-describe from HEAD, returns formated string (<major>.<minor>.<patch>.<misc>-<prerelease>+<upcount>#branch=<branch>.git=<hash>).

	Beware: Pre-existing <upcount> is resetted and <metadata> is stripped!
	'''

	formatted_version_string = None
	git                      = git_repo.git
	regexp                   = re.compile(version_prefix + '(\d+)\.(\d+)\.(\d+)(\.(\d+))?(\-(\D[\w\d\.]*))?(\!([\w\d\.]+))?(\#([\w\d\=\.]+))?(\-(\d+))?(\-g([0-9a-f]+))?(\-(dirty))?')


	try:
		git_description = str(git.execute(["git", "describe" , "--dirty"]))
	except:
		print ("Can not get git description!")
		raise

	# # for testing only:
	# git_description = "v0.0.10!dev-1-gcfbe8b6-dirty"

	print("Git description: " + git_description)

	version_regexped = re.search(regexp, git_description)

	print(version_regexped)

	# Do we have pre-existing Caveats?

	if version_regexped.group(9): # caveat
		caveat = str(version_regexped.group(9))
	else:
		caveat = None

	if version_regexped.group(13): # if upcount, add caveat "DEVELEOPMENT"
		if caveat:   # if we have pre-existings caveats ...
			caveat += "." + flag_development # ... append to caveats ...
		else:
			caveat = flag_development # ... otherwise set
	# Is workind dir dirty?

	# Repo.dirty has a bug returning dirty even when working directory is clean. Get state from git-describe instead.

	# if git_repo.is_dirty:
	if str(version_regexped.group(16)) == "-dirty":
		print("Repo is dirty!")
		if caveat:   # if we have pre-existings caveats ...
			caveat += "." + flag_dirty # ... append dirty to caveats ...
		else:
			caveat = flag_dirty # ... otherwise set do DIRTY

	formatted_version_string = (
		str(version_regexped.group(1)) +  # "major"
		"." +
		str(version_regexped.group(2)) +  # "minor"
		"." +
		str(version_regexped.group(3))   # "patch"
	)
	if version_regexped.group(5): # "misc"
		formatted_version_string += "." + str(version_regexped.group(5))
	if version_regexped.group(7): # "prerelease"
		formatted_version_string += "-" + str(version_regexped.group(7))
	if version_regexped.group(13): # "upcount"
		formatted_version_string += "+" + str(version_regexped.group(13))
	if caveat: # "caveat"
		formatted_version_string += "!" + caveat
	try:
		active_branch = str(git_repo.active_branch)
	except:
		active_branch = "NOBRANCH"

	if version_regexped.group(15): # "hash"
		formatted_version_string += (
			"#" +
			flag_branch +
			"=" +
			active_branch +
			"." +
			flag_git +
			"=" +
			str(version_regexped.group(15))
		)

	assert formatted_version_string, "formatted string is still empty!"

	return(formatted_version_string)

def parseVersionString(string:str):
	"""
	Takes a string and returns a list with version segment values:

	major, minor, patch, prerelease, upcount, caveat, metadata

	"""

	version_re = re.compile('(\d+)\.(\d+)\.(\d+)(\.(\d+))?(-([\w\d](([\w\d\.])*[\w\d])*))?(\!([\w\d](([\w\d\.])+[\w\d])*))?(\+(\d+)?(\!([\w\d]([\w\d\.])*[\w\d]))*)?(\#([\w\d](([\w\d\=\.])*[\w\d]))*)?')

	assert version_re.search(string), "Version string validation failed!"

	version_regexped = re.search(version_re, string)

	my_version = [
		version_regexped.group(1),  # "major" :
		version_regexped.group(2),  # "minor" :
		version_regexped.group(3),  # "patch" :
		version_regexped.group(5),  # "misc" :
		version_regexped.group(7),  # "prerelease" :
		version_regexped.group(15),  # "upcount" :
		version_regexped.group(17), # "caveat" :
		version_regexped.group(20) # "metadata" :
	]
	return(my_version)