#!/bin/python

def git_it(pkg_name):
    import os
    aur_git_url = 'https://aur.archlinux.org';
    os.system('git clone {}/{}.git'.format(aur_git_url, pkg_name))


if __name__ == '__main__':
    import sys

    av = sys.argv[1:]
    if len(av) == 0 or av[0]=='':
        print('Usage: aur-git <package_name>')
        exit(1)

    git_it(av[0])
