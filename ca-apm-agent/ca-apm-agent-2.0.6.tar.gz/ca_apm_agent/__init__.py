__copyright__ = """
* Copyright (c) 2018 CA. All rights reserved.
*
* This software and all information contained therein is confidential and proprietary and
* shall not be duplicated, used, disclosed or disseminated in any way except as authorized
* by the applicable license agreement, without the express written permission of CA. All
* authorized reproductions must be marked with this language.
*
* EXCEPT AS SET FORTH IN THE APPLICABLE LICENSE AGREEMENT, TO THE EXTENT
* PERMITTED BY APPLICABLE LAW, CA PROVIDES THIS SOFTWARE WITHOUT WARRANTY
* OF ANY KIND, INCLUDING WITHOUT LIMITATION, ANY IMPLIED WARRANTIES OF
* MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT WILL CA BE
* LIABLE TO THE END USER OR ANY THIRD PARTY FOR ANY LOSS OR DAMAGE, DIRECT OR
* INDIRECT, FROM THE USE OF THIS SOFTWARE, INCLUDING WITHOUT LIMITATION, LOST
* PROFITS, BUSINESS INTERRUPTION, GOODWILL, OR LOST DATA, EVEN IF CA IS
* EXPRESSLY ADVISED OF SUCH LOSS OR DAMAGE.
"""
import os
import errno
import getopt
import sys
from ca_apm_agent.global_constants import PRINT_PREFIX, CONTAINERID

import subprocess

def getcontainerid():
    temp = None
    containerid = None
    temp = subprocess.check_output(
            "grep docker -m1 /proc/self/cgroup|echo $(read s;s=${s##*/};s=${s#*docker-};s=${s%.scope};echo $s)",
            shell=True)
    containerid = temp.decode()
    if containerid == '\n':
       containerid = None
    else:
       containerid = containerid.strip('\n')
       
    return containerid

environ = os.environ

#
# To add more options follow the strategy below
# #Short Options
# options with an equivalent long name are to be added to the start of the short_opt_string
# options without an equivalent long name are to be appended to the short_opt_string
# #Long Options
# options with an equivalent short name are to be added to the start of the long_opt_list
# options without an equivalent short name are to be appended to the long_opt_list
#
short_opt_string = 'ha:i:d'
long_opt_list = ['help', 'agent-config=', 'instrumentation-config=', ]


def parse_opts(optlist):
    from ca_apm_agent.global_constants import CA_APM_PYTHON_ACFG, CA_APM_PYTHON_ICFG
    for opt, args in optlist:
        if opt in ('-h', '--help'):
            print (extended_usage())
            return True
        # Add options with both names after this comment
        elif opt in ('-a', '--agent-config'):
            environ[CA_APM_PYTHON_ACFG] = os.path.realpath(os.path.expanduser(args))
        elif opt in ('-i', '--instrumentation-config'):
            environ[CA_APM_PYTHON_ICFG] = os.path.realpath(os.path.expanduser(args))
        # Add options with only short names after this comment
        elif opt == '-d':
            # TODO enable debugging
            pass
        # Add options with only long names after this comment
        else:
            print_usage()
            return True
    return False


def print_usage():
    print (PRINT_PREFIX + '\n' \
            'For default usage: ca-apm-runpy <your existing command>\n ' \
            'For advanced usage ca-apm-runpy -h/--help')


def extended_usage():
    print (PRINT_PREFIX + '\n' \
          'For default usage                   :  ca-apm-runpy <your existing command>\n ' \
          'Advanced usage                      :  ca-apm-runpy <options> <your existing command>\n ' \
          'Available options \n' \
          '-h/--help                           :  Gets you back to this message \n' \
          '-a/--agent-config <file>            :  Custom agent configuration file \n' \
          '-i/--instrumentation config <file>  :  Custom instrumentation configuration file \n' \
          '' \
          'See documentation for details \n')


def main():
    args = sys.argv[1:]
    optlist, target = getopt.getopt(args, short_opt_string, long_opt_list)

    # option parsing
    help_quit = parse_opts(optlist)
    # get containerId and store in environ for further retrieval
    environ[CONTAINERID] = str(getcontainerid())

    # bootstrap environment and target loading
    if not help_quit:
        print (PRINT_PREFIX + 'Setting up Environment')
        import ca_apm_agent.bootstrap
        pythonpath = [os.path.dirname(ca_apm_agent.bootstrap.__file__)]

        from ca_apm_agent.global_constants import PYTHONPATH, PYTHONUNBUFFERED, PYTHONVERBOSE
        if PYTHONPATH in environ:
            pythonpath.append(environ[PYTHONPATH])
        environ[PYTHONPATH] = ':'.join(pythonpath)

        environ[PYTHONUNBUFFERED] = 'True'
        # environ[PYTHONVERBOSE] = 'True'

        try:
            print (PRINT_PREFIX + 'Attempting to Bootstrap and Run "' + ' '.join(args) + '"')
            os.execvpe(target[0], target, environ)
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                print (PRINT_PREFIX + '%s: no such file or directory' % target[0])
            elif exc.errno == errno.EPERM:
                 print (PRINT_PREFIX + '%s: permission denied' % target[0])
            raise
