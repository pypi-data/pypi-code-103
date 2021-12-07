# The MIT License (MIT)
#
# Copyright (c) 2016-2021 Thorsten Simons (sw@snomis.eu)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import cmd
import logging
import os
import sys
import time
from collections import OrderedDict
from pprint import pprint
from threading import Lock
import boto3
import botocore
from boto3.s3.transfer import S3Transfer, TransferConfig
from botocore.client import Config
from botocore.utils import fix_s3_host
from glob import glob
import click

from hs3 import calctime, _print, calcByteSize, _
import hs3.init
import hs3.conf
import hs3.parse
from hs3.s3config import ConfigItems

PIPE = '|'  # output shall be piped
OUTFILE = '>'  # output shall be written to a file
EXTENDFILE = '>>'  # output shall extend a file
S_IFDIR =  0o040000 # used to identify a directory...


# noinspection PyUnresolvedReferences
class HS3shell(cmd.Cmd):
    intro = hs3.init.INTRO

    prompt = '--> '

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rlogger = logging.getLogger()
        self.logger = logging.getLogger(__name__)
        self.progress = True  # show progress bar if True
        self.endpoint = None  # the S3 endpoint
        self.mode = None  # 'aws' or 'compatible'
        self.ssl = True  # if https shall be used
        self.session = None  # the boto3 session
        self.s3 = None  # the connection
        self.bucket = None  # the bucket object to work with
        self.bucketname = None  # its name
        self.encrypted = False  # if objects shall be server side encrypted
        self.profiles = None  # a dict of dicts per profile in .hs3sh.conf
        self.profile = None  # the profile in use
        self._config = None  # the AWS authentication config
        self.confitems = ConfigItems()


    def cmdloop(self, intro=None):
        """
        This is to allow to interrupt running commands via KeyboardInterrupt
        (CTRL-C); this will kill the commandloop, so we make sure it is
        restarted right away.
        """
        while True:
            try:
                super(HS3shell, self).cmdloop(intro=intro)
                break
            except (KeyboardInterrupt, click.exceptions.Abort):
                _print("^C", err=True)
            except AttributeError as e:
                _print('error: invalid command...',
                       'hint: {}' .format(e), err=True)
            except BrokenPipeError as e:
                # In case we started an external command through a pipe, and
                # this one failed we end up with a broken pipe. We need to work
                # around this to get back into a stable state using stdout.
                _print('error: running external command failed',
                       'hint: {}' .format(e), err=True)
                self.postcmd(False, '')

    def preloop(self):
        # read the configuration file(s)
        try:
            self.profiles = hs3.conf.readconf()
        except Exception as e:
            sys.exit('error: no config file loaded...\n\thint: {}'.format(e))

        # if we have a ~/.hs3shrc file, read it and execute the commands...
        # noinspection PyBroadException
        try:
            startupfile = os.path.join(os.path.expanduser("~"), ".hs3shrc")
            with open(startupfile, 'r') as inhdl:
                for cmnd in inhdl.readlines():
                    cmnd = cmnd.strip()
                    # skip comments and empty lines
                    if cmnd and not cmnd.startswith('#'):
                        self.cmdqueue.append('_exec ' + cmnd.strip())
        except Exception:
            pass

    def precmd(self, arg):
        """
        This overwrites the pre-command hook to strip off redirections from a
        command and sys.stdout accordingly accordingly.

        We are relying on everything being printed to sys.std. We realize
        redirections by simply mapping sys.stdout to a different file handle.

        :param arg:     the paramaters given with the command
        :return:        the command w/o the redirection or an empty string
                        if parsing failed
        """

        # detect EOF
        if arg == 'EOF':
            return('bye')


        # first let's see if we need to look for pipe/outfile
        redir_type = redir_arg = None
        try:
            if arg.find(EXTENDFILE) != -1:
                redir_type = EXTENDFILE
                arg, redir_arg = arg.split(EXTENDFILE)
                redir_arg = redir_arg.strip()
            elif arg.find(OUTFILE) != -1:
                redir_type = OUTFILE
                arg, redir_arg = arg.split(OUTFILE)
                redir_arg = redir_arg.strip()
            elif arg.find(PIPE) != -1:
                redir_type = PIPE
                arg, redir_arg = arg.split(PIPE)
                redir_arg = redir_arg.strip()
        except Exception as e:
            _print('parsing redirction failed...\nhint: {}'.format(e))
            return ''

        if redir_type and arg.split()[0] in hs3.init.no_redir_cmds:
            _print('error: no redirection for command "{}"...'
                  .format(arg.split()[0]))
            return ''

        if redir_type and not redir_arg:
            _print('error: redirection without arguments...')
            return ''

        if redir_type == PIPE:
            try:
                sys.stdout = os.popen(redir_arg, 'w')
            except Exception as e:
                _print('redirection error...\nhint: {}'.format(e))
                return ''
        elif redir_type == OUTFILE:
            try:
                sys.stdout = open(redir_arg, 'w')
            except Exception as e:
                _print('redirection error...\nhint: {}'.format(e))
                return ''
        elif redir_type == EXTENDFILE:
            try:
                sys.stdout = open(redir_arg, 'a')
            except Exception as e:
                _print('redirection error...\nhint: {}'.format(e))
                return ''

        return arg

    def postcmd(self, stop, line):
        """
        This overwrites the ppst-command hook to reset sys.stdout to what it
        should be after a command with redirection was executed.
        """
        # make sure we flush the file handle to which sys.stdout points to at
        # the moment.
        print('', end='', flush=True)
        if sys.stdout != sys.__stdout__:
            sys.stdout.close()
            sys.stdout = sys.__stdout__
        return stop

    def emptyline(self):
        """Disable repetition of last command by pressing Enter"""
        pass

    def do_debug(self, args):
        'debug [cmd [args]]\n' \
        '    Without "cmd [args]", toggle debug mode,\n' \
        '    with "cmd [args]", toggle debug mode for that command, only.'

        lvl = self.rlogger.getEffectiveLevel()
        _print('toggeled logging from {} to '
              .format('ERROR' if lvl == 40 else 'DEBUG'), nl='')
        if self.rlogger.getEffectiveLevel() == logging.ERROR:
            self.rlogger.setLevel(logging.DEBUG)
        else:
            self.rlogger.setLevel(logging.ERROR)
        _print('{}'.format('ERROR' if self.rlogger.getEffectiveLevel() == 40 else 'DEBUG'))

        if len(args):
            self.cmdqueue.append(args)
            self.cmdqueue.append('debug')

    def do__exec(self, arg):
        # Run a command given as parameters, but make sure to _print a prompt
        # before. This is for running scripted commands (~/.hs3shrc)

        self.logger.debug('--> called "_run {}"'.format(arg))

        p = arg.split(maxsplit=1)
        command, params = p if len(p) > 1 else (arg, '')

        if command:
            # _print(self.prompt + arg, flush=True)
            _print(self.prompt + arg)
            return eval('self.do_{}("{}")'.format(command, params))
        else:
            return

    def do_acl(self, arg):
        'acl -b|-o name [-g user permission [, user permission]* '\
        '[-s canned ACL]\n' \
        '    Set Access Control Lists on a bucket or an object\n' \
        '    -b name = bucket\n' \
        '    -o name = object (needs to start with a "/"\n' \
        '    -g set per-user permission(s)\n' \
        '       permissions is one of full_control, write, write_acp,\n' \
        '       read, read_acp\n' \
        '    -s set canned ACL\n' \
        '       a canned ACLs is one of private, public-read,\n' \
        '       public-read-write, authenticated-read\n' \
        '    user is either:\n' \
        '       **for AWS**: a user\'s canonical ID\n' \
        '       **for HCP**: a local HCP user name or an Active Directory '\
        'user\n' \
        '       (if HCP is integrated with AD) like this: aduser@domain.com\n' \
        '       **for other S3 storage**: refer to the respective manual on '\
        'how to\n' \
        '       specify its users\n' \
        '       and **for all S3 stores**: one of allusers, authenticateduser,'\
        ' logdelivery\n' \
        '\n' \
        '*   If neither -g nor -s is given, list the actual ACLs\n' \
        '*   -g and -s are exclusive\n' \
        '*   If any specifier holds characters outside the ascii alphabet and '\
        'the\n' \
        '    underscore, surrond it with "quotation marks"'

        self.logger.info('--> called "acl {}"'.format(arg))

        if not self.profile:
            _print('error: you need to connect, first...', err=True)
            return

        try:
            para = hs3.parse.parse_acl(arg)
        except Exception as e:
            _print('error: while parsing parameters...\nhint: {}'.format(e),
                  err=True)
            return
        else:
            if hs3.parse.OBJECT in para.flags and not self.bucket:
                _print('error: you need to attach a bucket, first...',
                      err=True)
                return

        if para.isbucket:  # working on a bucket
            try:
                acl = self.s3.Bucket(para.name).Acl()
                acl.load()
            except Exception as e:
                _print('error: unable to access bucket ACLs...\nhint: {}'
                       .format(e), err=True)
                return
            else:
                # we just list what we have
                if hs3.parse.GRANT not in para.flags and not para.canned:
                    _print('ACLs for bucket {}'.format(para.name))
                    out = {'Owner': acl.owner, 'Grants': acl.grants}
                    pprint(out)
                elif para.canned and para.pairs:
                    _print('error: -g and -s are exclusive...')
                elif para.canned:
                    # set canned ACL
                    if para.canned:
                        try:
                            acl.put(ACL=para.canned)
                        except Exception as e:
                            _print('error: setting a canned bucket ACL failed.'
                                   '..\nhint: {}'.format(e), err=True)
                elif para.pairs:
                    newgrants = acl.grants

                    for g, p in para.pairs:
                        if g.lower() in hs3.init.AWSGROUPS.keys():
                            newgrants.append(
                                {'Grantee': {'URI': hs3.init.AWSGROUPS[g.lower()],
                                             'Type': 'Group',
                                             },
                                 'Permission': p})
                        else:
                            newgrants.append(
                                # {'Grantee': {'EmailAddress': g,
                                #              'Type': 'AmazonCustomerByEmail',
                                #              },
                                #  'Permission': p})
                                {'Grantee': {'ID': g,
                                             'Type': 'CanonicalUser',
                                             },
                                 'Permission': p})

                    # To make sure we apply to the XSD found at
                    # https://admin.<yourhcp>.<yourdomain>.<tld>/static/xsd/AmazonS3.xsd,
                    # we need to sort all the entries accordingly
                    aclowner, newgrants = hs3.parse.aclcleanup(acl.owner, newgrants)

                    try:
                        _ACP = OrderedDict([('Owner', aclowner),
                                            ('Grants', newgrants)])
                        acl.put(AccessControlPolicy=_ACP)
                    except Exception as e:
                        _print(
                            'error: setting per-user bucket ACL failed...'
                            '\nhint: {}'.format(e), err=True)
        else:  # working on an object
            try:
                if not para.version:
                    acl = self.s3.Object(self.bucketname, para.name).Acl()
                    acl.load()
                else:
                    acl = self.s3.ObjectVersion(self.bucketname, para.name, para.version).Object().Acl()
                    acl.load()
            except Exception as e:
                _print('error: unable to access bucket ACLs...\nhint: {}'
                       .format(e), err=True)
                return
            else:
                if hs3.parse.GRANT not in para.flags and not para.canned:
                    _print('ACLs for object {} {}'
                          .format(para.name,
                                  'v.'+para.version if para.version else ''))
                    out = {'Owner': acl.owner, 'Grants': acl.grants}
                    pprint(out)
                elif para.canned and para.pairs:
                    _print('error: -g and -s are exclusive...')
                elif para.canned:
                    # set canned ACL
                    if para.canned:
                        try:
                            acl.put(ACL=para.canned)
                        except Exception as e:
                            _print('error: setting a canned object ACL failed.'
                                   '..\nhint: {}'.format(e), err=True)

                elif para.pairs:
                    newgrants = acl.grants

                    for g, p in para.pairs:
                        if g.lower() in hs3.init.AWSGROUPS.keys():
                            newgrants.append(
                                {'Grantee': {'URI': hs3.init.AWSGROUPS[g.lower()],
                                             'Type': 'Group',
                                             },
                                 'Permission': p})
                        else:
                            newgrants.append(
                                {'Grantee': {'ID': g,
                                             'Type': 'CanonicalUser',
                                             },
                                 'Permission': p})

                    # To make sure we apply to the XSD found at
                    # https://admin.<yourhcp>.<yourdomain>.<tld>/static/xsd/AmazonS3.xsd,
                    # we need to sort all the entries accordingly
                    aclowner, newgrants = hs3.parse.aclcleanup(acl.owner, newgrants)

                    try:
                        _ACP = OrderedDict([('Owner', aclowner),
                                            ('Grants', newgrants)])
                        acl.put(AccessControlPolicy=_ACP)
                    except Exception as e:
                        _print(
                            'error: setting per-user object ACL failed...'
                            '\nhint: {}'.format(e), err=True)


    def do_attach(self, bucket):
        'attach <bucket_name>\n' \
        '    Attaches the bucket to be used by further commands. Think of\n' \
        '    change directory...'
        self.logger.info('--> called "attach {}"'.format(bucket))

        if not self.profile:
            _print('error: you need to connect, first...', err=True)
            return

        try:
            self.bucket = self.s3.Bucket(bucket)
            # switch this of, as it causes an error (404) when attaching a
            # bucket which is not owned by this user
            # self.bucket.load()
        except Exception as e:
            _print('error: attach of bucket "{}" failed\nhint: {}'
                   .format(bucket, e), err=True)
        else:
            self.bucketname = bucket

    def do_bucket(self, arg):
        'bucket [-c|-cv|-r|-v] bucketname\n' \
        '    create or remove a bucket\n' \
        '    -c create <bucketname>\n' \
        '    -r remove bucket (needs to be empty)\n' \
        '    -v toggle versioning\n' \
        '    without any flags, the bucket\'s versioning status is shown'
        self.logger.info('--> called "bucket {}"'.format(arg))

        if not self.profile:
            _print('error: you need to connect, first...', err=True)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='cvr')
        except Exception as e:
            _print('error: while parsing parameters...\nhint: {}'.format(e),
                  err=True)
            return
        else:
            if not len(para.args):
                _print('error: no bucketname specified...', err=True)
                return
            else:
                bucket = para.args[0]
            if 'v' in para.flags and 'r' in para.flags:
                _print('error: -v not possible with -r', err=True)
                return

            if 'c' in para.flags:  # create bucket
                try:
                    bkt = self.s3.Bucket(bucket)
                    eval('bkt.create({})'.format(
                        'CreateBucketConfiguration={"LocationConstraint": "' +
                        self.profiles[self.profile]['region'] + '"}' if
                        self.profiles[self.profile]['region'] else ''))
                except Exception as e:
                    _print('error: create bucket failed...\nhint: {}'
                           .format(e), err=True)
                else:
                    if 'v' in para.flags:
                        try:
                            bv = bkt.Versioning()
                            bv.enable()
                        except Exception as f:
                            _print(
                                'error: enabling versioning failed...\n'
                                'hint: {}'.format(f), err=True)
                return
            if 'r' in para.flags:  # remove bucket
                try:
                    bkt = self.s3.Bucket(bucket)
                    bkt.delete()
                except Exception as e:
                    _print(
                        'error: delete bucket failed...\nhint: {}'.format(e),
                        err=True)
                return

            # get info about versioning status
            try:
                bkt = self.s3.Bucket(bucket)
                bv = bkt.Versioning()
            except Exception as e:
                _print('error: can\'t get versioning status...\nhint: {}'
                       .format(e), err=True)
                return

            if 'v' in para.flags and 'c' not in para.flags:
                # toggle versioning
                try:
                    if bv.status == 'Enabled':
                        bv.suspend()
                        bv.reload()
                        _print('versioning is now {}'.format(
                            bv.status.lower() if bv.status else 'disabled'))
                    else:
                        bv.enable()
                        bv.reload()
                        _print('versioning is now {}'.format(
                            bv.status.lower() if bv.status else 'disabled'))
                    return
                except Exception as e:
                    _print('error: can\'t toggle versioning status...\nhint: {}'
                           .format(e), err=True)
                    return

            if not para.flags:  # show bucket status
                try:
                    _print('versioning status: {}'.format(
                        bv.status.lower() if bv.status else 'disabled'))
                except Exception as e:
                    _print('error: can\'t get versioning status...\nhint: {}'
                           .format(e), err=True)
                return
        _print('error: invalid parameters...', err=True)
        return

    def do_bye(self, arg):
        'Exit hs3sh gracefully.'
        self.logger.info('--> called "bye {}"'.format(arg))

        _print('Ending gracefully...')
        return True

    def do_connect(self, arg):
        'connect <profile_name>\n' \
        '    Connect to an S3 endpoint using profile <profile_name>\n' \
        '    from ~/.hs3sh.conf or ./.hs3sh.conf'
        self.logger.info('--> called "connect {}"'.format(arg))

        try:
            para = hs3.parse.paramcheck(arg, flags='')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                  err=True)
            return
        else:
            if len(para.args) != 1:
                _print(
                    'error: a profile_name as explicit parameter is required',
                    err=True)
                return
            if para.args[0] not in self.profiles.keys():
                _print('error: unknown profile: {}'.format(para.args[0]),
                      err=True)
                return
            else:
                self.profile = para.args[0]
                self.mode = self.profiles[self.profile]['type']

            self.logger.debug('using profile {}'
                              .format(self.profiles[self.profile]))

            # setup a Config object
            self._config = Config(s3={'addressing_style': 'path',
                                      'payload_signing_enabled': self.profiles[self.profile]['payload_signing_enabled']},
                                  signature_version=self.profiles[self.profile]['signature_version'])
            try:
                if self.mode == 'aws':
                    self.session = boto3.session.Session(
                        aws_access_key_id=self.profiles[self.profile][
                            'aws_access_key_id'],
                        aws_secret_access_key=self.profiles[self.profile][
                            'aws_secret_access_key'],
                        region_name=self.profiles[self.profile]['region'])
                    self.s3 = self.session.resource('s3', config=self._config)
                else:
                    endpoint = ('https://' if self.profiles[self.profile][
                        'https'] else 'http://') + self.profiles[self.profile][
                                   'endpoint']
                    if self.profiles[self.profile]['port']:
                        endpoint = '{}:{}'.format(endpoint,
                                                  self.profiles[self.profile][
                                                      'port'])
                    self.logger.debug('endpoint is "{}"'.format(endpoint))
                    self.session = boto3.session.Session(
                        aws_access_key_id=self.profiles[self.profile][
                            'aws_access_key_id'],
                        aws_secret_access_key=self.profiles[self.profile][
                            'aws_secret_access_key'],
                        region_name=self.profiles[self.profile]['region'])
                    self.s3 = self.session.resource('s3',
                                                    endpoint_url=endpoint,
                                                    verify=False,
                                                    config=self._config)
                    self.s3.meta.client.meta.events.unregister(
                        'before-sign.s3',
                        fix_s3_host)
            except Exception as e:
                _print('error: connect failed\nhint: {}'.format(e),
                      err=True)
            else:
                self.bucket = self.bucketname = None

    def do_cp(self, arg):
        'cp [-v version_id] source target ["metakey:metavalue"]*\n' \
        '    Request the S3 service to perform a server-side copy of (a '\
        'defined\n' \
        '    version_id of) source to target object, replacing eventually\n' \
        '    existing source metadata pairs with the named metadata pairs,\n' \
        '    if given; else copy the existing metadata pairs, along with the\n'\
        '    object.\n\n' \
        '    You can use the copy command to copy the source object to\n' \
        '    itself to create a new version of the source object with\n' \
        '    changed metadata pairs.'
        self.logger.info('--> called "cp {}"'.format(arg))

        if not self.profile:
            _print('error: you need to connect, first...', err=True)
            return

        if not self.bucket:
            _print('error: you need to attach to a bucket, first...',
                  err=True)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='v', meta=True)
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   err=True)
            return
        else:
            _version = True if 'v' in para.flags else False
            if len(para.args) < (3 if _version else 2):
                _print('error: at least {} parameter are required'
                      .format('three' if _version else 'two'), err=True)
                return
            else:
                if 'v' in para.flags:
                    _ver = para.args[0]
                    _src = para.args[1]
                    _tgt = para.args[2]
                else:
                    _ver = None
                    _src = para.args[0]
                    _tgt = para.args[1]

        try:
            obj = self.s3.Object(self.bucketname, _tgt)
            if para.metadict:
                response = obj.copy_from(CopySource={'Bucket': self.bucketname,
                                                     'Key': _src,
                                                     'VersionId': _ver},
                                         Metadata=para.metadict,
                                         MetadataDirective='REPLACE')
            else:
                response = obj.copy_from(CopySource={'Bucket': self.bucketname,
                                                     'Key': _src,
                                                     'VersionId': _ver},
                                         MetadataDirective='COPY')
            if 'CopySourceVersionId' in response:
                _print('CopySourceVersionId: {}'
                      .format(response['CopySourceVersionId']))
            if 'VersionId' in response:
                _print('          VersionId: {}'.format(response['VersionId']))
        except Exception as f:
            _print('error: copy_from failed...\nhint: {}'.format(f),
                   err=True)

    def do_get(self, arg):
        'get [-m] [-v version_id] object [localfile]\n' \
        '    Get (read) an object and _print it.\n' \
        '    -m request MultiPartDownload,\n' \
        '    -v get object version instead of the latest version\n' \
        '    If localfile is specified, store the object to it.'
        self.logger.info('--> called "get {}"'.format(arg))

        if not self.profile:
            _print('error: you need to connect, first...', err=True)
            return

        if not self.bucket:
            _print('error: you need to attach to a bucket, first...',
                  err=True)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='mv', meta=False)
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   err=True)
            return
        else:
            _version = True if 'v' in para.flags else False
            if len(para.args) < (2 if _version else 1):
                _print('error: at least {} parameter are required'
                      .format('two' if _version else 'one'), err=True)
                return
            else:
                if 'm' in para.flags and 'v' in para.flags:
                    _print('error: multipart download not supported for versions',
                          err=True)
                    return
                elif _version:
                    _ver = para.args[0]
                    _src = para.args[1]
                    _tgt = para.args[2] if len(para.args) > 2 else para.args[0].split('/')[-1]
                else:
                    _ver = None
                    _src = para.args[0]
                    _tgt = para.args[1] if len(para.args) > 1 else para.args[0].split('/')[-1]

            # first need to find out the size of the object to be able to
            # display the progress bar
            try:
                    obj = self.s3.Object(self.bucketname, _src)
                    obj.load()
                    _src_size = obj.content_length
            except Exception as e:
                _print('error: reading object metadata failed...\nhint: {}'.format(e),
                       err=True)
                return

            try:
                if self.mode == 'aws':
                    cl = self.session.client('s3',
                                             aws_access_key_id=
                                             self.profiles[self.profile][
                                                 'aws_access_key_id'],
                                             aws_secret_access_key=
                                             self.profiles[self.profile][
                                                 'aws_secret_access_key'],
                                             region_name=
                                             self.profiles[self.profile][
                                                 'region'],
                                             config=self._config)
                else:
                    endpoint = ('https://' if self.profiles[self.profile][
                        'https'] else 'http://') + \
                               self.profiles[self.profile]['endpoint']
                    if self.profiles[self.profile]['port']:
                        endpoint = '{}:{}'.format(endpoint,
                                                  self.profiles[self.profile][
                                                      'port'])
                    cl = self.session.client('s3',
                                             aws_access_key_id=
                                             self.profiles[self.profile][
                                                 'aws_access_key_id'],
                                             aws_secret_access_key=
                                             self.profiles[self.profile][
                                                 'aws_secret_access_key'],
                                             endpoint_url=endpoint,
                                             verify=False,
                                             config=self._config)
                    cl.meta.events.unregister('before-sign.s3',
                                              fix_s3_host)
            except Exception as e:
                _print('error: get failed...\nhint: {}'.format(e),
                       err=True)
                return

            # multipart download wanted ?
            _mp_threshold = self.confitems.mpu_size if 'm' in para.flags else _src_size+1

            try:
                transconf = TransferConfig(multipart_threshold=_mp_threshold,
                                           max_concurrency=self.confitems.mpu_threads,
                                           multipart_chunksize=self.confitems.mpu_size,
                                           # we go with the defaults for the remainder
                                           # num_download_attempts=5,
                                           # max_io_queue=100,
                                           # io_chunksize=262144,
                                           # use_threads=True
                                           )
                transfer = S3Transfer(client=cl, config=transconf)
                if self.progress:
                    with click.progressbar(length=_src_size, show_eta=True, show_percent=True, show_pos=True,
                                           label=f'GET {".." + _src[-20:] if len(_src) > 22 else _src} ') as bar:
                        transfer.download_file(self.bucketname, _src, _tgt, callback=bar.update)
                else:
                    transfer.download_file(self.bucketname, _src, _tgt)

            except Exception as e:
                _print('error: transfer failed...\nhint: {}'.format(e),
                       err=True)
                return

    def do_getbl(self, arg):
        'getbl <bucket>\n' \
        '    Get (read) the bucket location for <bucket>.'
        self.logger.info('--> called "getbucketlocation {}"'.format(arg))

        if not self.profile:
            _print('error: you need to connect, first...', err=True)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   err=True)
            return
        if len(para.args) != 1:
            _print('error: parameters invalid...\nhint: one parameter required',
                   err=True)
            return

        try:
            if self.mode == 'aws':
                cl = self.session.client('s3',
                                         aws_access_key_id=
                                         self.profiles[self.profile][
                                             'aws_access_key_id'],
                                         aws_secret_access_key=
                                         self.profiles[self.profile][
                                             'aws_secret_access_key'],
                                         region_name=
                                         self.profiles[self.profile][
                                             'region'],
                                         config=self._config)
            else:
                endpoint = ('https://' if self.profiles[self.profile][
                    'https'] else 'http://') + \
                           self.profiles[self.profile]['endpoint']
                if self.profiles[self.profile]['port']:
                    endpoint = '{}:{}'.format(endpoint,
                                              self.profiles[self.profile][
                                                  'port'])
                cl = self.session.client('s3',
                                         aws_access_key_id=
                                         self.profiles[self.profile][
                                             'aws_access_key_id'],
                                         aws_secret_access_key=
                                         self.profiles[self.profile][
                                             'aws_secret_access_key'],
                                         endpoint_url=endpoint,
                                         verify=False,
                                         config=self._config)
                cl.meta.events.unregister('before-sign.s3',
                                          fix_s3_host)
        except Exception as e:
            _print('error: failed...\nhint: {}'.format(e),
                   err=True)
            return

        try:
            response = cl.get_bucket_location(Bucket=para.args[0])
        except Exception as e:
            _print('error: get_bucket_location() failed...\nhint: {}'.format(e),
                   err=True)
            return
        else:
            _print(response['LocationConstraint'])


    def do_help(self, arg):
        'List available commands with "help" or detailed help with "help cmd".'

        # This is the original code of the method; it needed to be overwritten
        # to get rid of listing undocumented commands.
        if arg:
            # XXX check arg syntax
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    doc = getattr(self, 'do_' + arg).__doc__
                    if doc:
                        self.stdout.write("%s\n" % str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n" % str(self.nohelp % (arg,)))
                return
            func()
        else:
            names = self.get_names()
            cmds_doc = []
            cmds_undoc = []
            help = {}
            for name in names:
                if name[:5] == 'help_':
                    help[name[5:]] = 1
            names.sort()
            # There can be duplicates if routines overridden
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    command = name[3:]
                    if command in help:
                        cmds_doc.append(command)
                        del help[command]
                    elif getattr(self, name).__doc__:
                        cmds_doc.append(command)
                    else:
                        cmds_undoc.append(command)
            self.stdout.write("%s\n" % str(self.doc_leader))
            self.print_topics(self.doc_header, cmds_doc, 15, 80)
            self.print_topics(self.misc_header, list(help.keys()), 15, 80)
            # self.print_topics(self.undoc_header, cmds_undoc, 15, 80)


    def do_lcd(self, args):
        'lcd [local-directory]\n'\
        '    change the local working directory to local-directory (or to\n'\
        '    home directory, if local-directory isn\'t given)'
        self.logger.info('--> called "lcd {}"'.format(args))
        try:
            para = hs3.parse.paramcheck(args, flags='')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if len(para.args) > 1:
                _print('error: at max 1 parameter is allowed...',
                       err=True)
                return
            else:
                newd = para.args[0] if len(para.args) else os.path.expanduser("~")
                try:
                    os.chdir(newd)
                except Exception as e:
                    _print('LCWD failed: {}'.format(e), err=True)
                    return
                _print('LCWD command{}successful.'
                       .format(' to {} '.format(newd) if not len(para.args) else ' '))


    def do_lls(self, arg):
        'lls [local-path]\n'\
        '    list contents of local path'
        self.logger.info('--> called "lls {}"'.format(arg))
        try:
            para = hs3.parse.paramcheck(arg)
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if len(para.args) > 1:
                _print('error: at max one parameter required...', err=True)
                return
            else:
                if len(para.args):
                    try:
                        isdir = True if os.stat(para.args[0]).st_mode & S_IFDIR == S_IFDIR else False
                    except FileNotFoundError:
                        cwd = para.args[0]
                    else:
                        cwd = join(para.args[0], '*') if isdir else para.args[0]
                else:
                    cwd = '*'

        for f in sorted(glob(cwd)):
            # drwxr-xr-x   1 root  users   4096 May  9 14:47 hcp_a
            # -rwxrwxrwx   1 admin users  14656 May 04  2015 2013 IP-Umstellung.ods
            st = os.stat(f)
            _print('{} {:>4} {:8} {:8} {:>12} {} {}'
                   .format(self.__mode(st.st_mode),
                           st.st_nlink,
                           os.getuid(),
                           os.getuid(),
                           calcByteSize(st.st_size),
                           time.strftime('%Y/%m/%d %H:%M:%S',
                                         time.localtime(st.st_mtime)),
                           f))


    def do_lpwd(self, args):
        'lpwd\n'\
        '    Print the local working directory.'
        self.logger.info('--> called "lpwd {}"'.format(args))
        _print('Local directory: {}'.format(self.__getcwd()))


    def do_ls(self, arg):
        'ls [-aemv] [prefix]\n' \
        '    List the objects within the active bucket.\n' \
        '    -a _print object acls,\n' \
        '    -e _print the objects etags,\n' \
        '    -m _print metadata pairs per object, if available,\n' \
        '    -v _print each object\'s versions, if there are some.\n' \
        '    If prefix is given, list objects starting with the prefifx, only.'
        self.logger.info('--> called "ls {}"'.format(arg))

        if not self.profile:
            _print('error: you need to connect, first...', err=True)
            return

        if not self.bucket:
            _print('error: you need to attach to a bucket, first...',
                  err=True)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='aemv')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   err=True)
            return

        if len(para.args) > 1:
            _print('error: maximal one parameter is allowed', err=True)
            return
        else:
            prefix = '' if not len(para.args) else para.args[0]

        _acl = True if 'a' in para.flags else False
        _etag = True if 'e' in para.flags else False
        _meta = True if 'm' in para.flags else False
        _versions = True if 'v' in para.flags else False

        try:
            if _versions:
                if _acl:
                    _print('{:>17} {:>15} {:36} {} {}'
                          .format('last modified',
                                  'size',
                                  'version_id                   grantee',
                                  'A',
                                  'object name/metadata    ACLs' if _meta else 'object name             ACLs'))
                else:
                    _print('{:>17} {:>15} {:36} {} {}'
                          .format('last modified', 'size', 'version_id', 'A',
                                  'object name/metadata' if _meta else 'object name'))
            else:
                if _acl:
                    _print('{:>17} {:>15} {:36} {}'
                          .format('last modified', 'size', 'version_id',
                                  'object name/metadata    ACLs' if _meta else 'object name             ACLs'))
                else:
                    _print('{:>17} {:>15} {:36} {}'
                          .format('last modified', 'size', 'version_id',
                                  'object name/metadata' if _meta else 'object name'))
            if _etag:
                _print('{:>17} {:>15} {:36}'.format('', '', 'etag'))

            _print(f'{"-"*17} {"-"*15} {"-"*36} {"-"*28}')

            # We have four different calls, depending on prefix and _versions
            # being asked for.
            if prefix:
                # this works for AWS, Cloudian and HCP
                # noinspection PyUnusedLocal
                query = self.bucket.objects.filter if not _versions else self.bucket.object_versions.filter
            else:
                # and this is required for ECS...
                # noinspection PyUnusedLocal
                query = self.bucket.objects.all if not _versions else self.bucket.object_versions.all

            for obj in eval('query({})'.format(('Prefix="' + prefix + '"')
                                               if prefix else '')):
                if not _versions:
                    obj = obj.Object()
                    obj.load()
                    # if not obj.last_modified:
                    #     setattr(obj, 'last_modified', time.localtime(0))
                    _print('{:>17} {:>15,} {:36} {}'
                          .format('?' if (
                    obj.last_modified == None) else obj.last_modified.strftime(
                        '%y/%m/%d-%H:%M:%S'),
                                  obj.size or 0 if _versions else obj.content_length or 0,
                                  _(obj.version_id,
                                    36) or 'null',
                                  obj.key))
                else:
                    # if not obj.last_modified:
                    #     setattr(obj, 'last_modified', time.localtime(0))
                    _print('{:>17} {:>15,} {:36} {} {}'
                          .format('?' if (
                    obj.last_modified == None) else obj.last_modified.strftime(
                        '%y/%m/%d-%H:%M:%S'),
                                  obj.size or 0 if _versions else obj.content_length or 0,
                                  _(obj.version_id,
                                    36),
                                  ' ' if not _versions
                                  else 'X' if obj.is_latest else ' ',
                                  obj.key))
                if _acl:
                    if _versions:
                        acl = obj.Object().Acl()
                    else:
                        acl = obj.Acl()
                    try:
                        acl.load()
                    except Exception as e:
                        self.logger.debug('get ACLs failed for key {} - {}'.format(obj.key, e))
                        _print(f'{"":17} {"":15} {"":>36} {""}{"n/a":>28}')
                    else:
                        for g in acl.grants:
                            if g['Grantee']['Type'] == 'CanonicalUser':
                                _f1 = ''
                                _f2 = g['Grantee']['DisplayName'] if 'DisplayName' in g['Grantee'].keys() else (g['Grantee']['ID'], 36)
                                _f3 = '  ' if _versions else ''
                                _f4 = g['Permission']
                                _print(f'{" "*17} {_f1:15} {_f2:>36} {_f3}{_f4:>28}')
                            elif g['Grantee']['Type'] == 'Group':
                                _f1 = ''
                                _f2 = g['Grantee']['URI'].split('/')[-1]
                                _f3 = '  ' if _versions else ''
                                _f4 = g['Permission']
                                _print(f'{" "*17} {_f1:15} {_f2:>36} {_f3}{_f4:28}')
                            else:
                                _print(f'{" "*17} unknown')
                try:
                    if _meta:
                        if _versions:
                            resp = obj.head()
                            if resp['Metadata']:
                                _print('{:>72} {}'.format('', resp['Metadata']))
                        else:
                            if obj.metadata:
                                _print('{:>70} {}'.format('', obj.metadata))
                except Exception as f:
                    _print(f, err=True)
                    pass

                if _etag:
                    _print('{:>17} {:>15} {:36}'
                          .format('', '', str(obj.e_tag).strip('"\'')))

        except Exception as e:
            # import traceback
            # traceback.print_exc()
            _print('error: ls failed\nhint: {}'.format(e), err=True)

    def do_lsb(self, arg):
        'lsb [-a]\n' \
        '    List the buckets available through the connected endpoint.\n' \
        '    -a shows ACLs as well.'
        self.logger.info('--> called "lsb {}"'.format(arg))

        if not self.profile:
            _print('error: you need to connect, first...', err=True)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='a')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   err=True)
            return

        _acls = True if 'a' in para.flags else False

        # test to get access to the region in AWS
        # if self.mode == 'aws':
        #     try:
        #         cl = botocore.session.Session().create_client('s3',
        #                                                       aws_access_key_id=
        #                                                       self.profiles[
        #                                                           self.profile][
        #                                                           'aws_access_key_id'],
        #                                                       aws_secret_access_key=
        #                                                       self.profiles[
        #                                                           self.profile][
        #                                                           'aws_secret_access_key'],
        #                                                       region_name=
        #                                                       self.profiles[
        #                                                           self.profile][
        #                                                           'region'])
        #     except Exception as e:
        #         _print('error: lsb failed...\nhint: {}'.format(e),
        #                err=True)
        #         return

        _print('{:>17} {:30} {:14} {} {:38}'
              .format('created',
                      'owner|ID' + (' '*15 + 'grantee' if _acls else ''),
                      'region', 'V',
                      'bucket name' + (' '*23 + 'ACLs' if _acls else ''),
                      ))
        _print(f'{"-"*17} {"-"*30} {"-"*14} - {"-"*38}')

        try:
            for b in self.s3.buckets.all():
                # noinspection PyUnboundLocalVariable
                # location = 'compatible' if self.mode != 'aws' else \
                #     cl.get_bucket_location(Bucket=b.name)['LocationConstraint']
                location = 'compatible' if self.mode != 'aws' else self.profiles[self.profile]['region']

                # get versioning status
                # noinspection PyBroadException
                try:
                    bv = b.Versioning()
                    version_state = 'X' if bv.status == 'Enabled' else ' '
                except Exception:
                    version_state = '?'

                try:
                    acl = b.Acl()
                    acl.load()
                    # noinspection PyBroadException
                    try:
                        owner = acl.owner['DisplayName']
                    except Exception:
                        owner = acl.owner['ID']
                    _print('{:17} {:30} {:14} {} {:38}'
                          .format(b.creation_date.strftime('%y/%m/%d-%H:%M:%S'),
                                  _(owner, 30), location,
                                  version_state, b.name))
                except botocore.exceptions.ClientError:
                    acl = None
                    if self.mode == 'aws':
                        _print('{:17} {:30} {:14} {} {:38}'
                              .format(
                            b.creation_date.strftime('%y/%m/%d-%H:%M:%S'),
                            '**not avail. through region**', location,
                            version_state, b.name))
                    else:
                        _print('{:17} {:30} {:14} {} {:38}'
                              .format(
                            b.creation_date.strftime('%y/%m/%d-%H:%M:%S'),
                            '**GetBucketAcl not impl.**', location,
                            version_state, b.name))

                if _acls and acl:
                    for g in acl.grants:
                        if g['Grantee']['Type'] == 'CanonicalUser':
                            _f1 = g["Grantee"]["DisplayName"] if "DisplayName" in g["Grantee"].keys() else _(g["Grantee"]["ID"], 30)
                            _f2 = ''
                            _f3 = g["Permission"]
                            _print(f'{" "*17} {_f1:>30} {_f2:14} {_f3:>40}')
                        elif g['Grantee']['Type'] == 'Group':
                            _f1 = g['Grantee']['URI'].split('/')[-1]
                            _f2 = ''
                            _f3 = g['Permission']
                            _print(f'{" "*17} {_f1:>30} {_f2:14} {_f3:>40}')
                        else:
                            _print(f'{" "*17} unknown')

        except Exception as e:
            _print('error: listing buckets failed...\nhint: {}'.format(e),
                   err=True)

    def do_lsp(self, arg):
        'lsp\n' \
        '    show the loaded profiles'
        self.logger.info('--> called "lsp {}"'.format(arg))

        _print('{:1} {:26} {:>8}  {}'.format('C', 'profile', 'tag', 'value'))
        _print('{:1} {:26} {:8}- {}'.format('-', '-'*26, '-'*8, '-'*39))
        for p in sorted(self.profiles.keys()):
            for tag in ['comment', 'endpoint', 'region', 'https']:
                if self.profiles[p][tag] or tag == 'https':
                    _print('{:1} {:26} {:>8}: {}'
                           .format('|' if p == self.profile else '',
                                   p if tag == 'comment' else '',
                                   tag,
                                   self.profiles[p][tag]))


    def do_progress(self, args):
        'progress\n'\
        '    toggle showing a progress meter on/off'
        self.logger.info('--> called "progress {}"'.format(args))
        self.progress = False if self.progress else True
        _print('Progress meter will {}be shown'
               .format('' if self.progress else 'not '))


    def do_put(self, arg):
        'put [-m] localfile object ["metakey:metavalue"]*\n' \
        '    Put (store) localfile as object into the attached bucket,\n' \
        '    adding metadata pairs, if specified.\n' \
        '    -m will try to do a multi-part put.'
        self.logger.info('--> called "put {}"'.format(arg))

        if not self.profile:
            _print('error: you need to connect, first...', err=True)
            return

        if not self.bucket:
            _print('error: you need to attach to a bucket, first...',
                  err=True)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='mcs', meta=True)
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   err=True)
            return
        else:
            if len(para.args) == 2:
                _src = para.args[0]
                _tgt = para.args[1]
            elif len(para.args) == 1:
                _src = para.args[0]
                _tgt = para.args[0].split('/')[-1]
            else:
                _print('error: source filename missing...')
                return
            _metadict = para.metadict

            # try to acquire the size of the file to PUT
            fsize = 0
            try:
                fsize = os.stat(_src).st_size
            except Exception as e:
                _print('warning: can\'t stat({})...\nhint: {}'.format(_src,
                                                                      e))
            else:
                _print('sending file "{}" of size {}'.format(_src, fsize))

            try:
                if self.mode == 'aws':
                    cl = self.session.client('s3',
                                             aws_access_key_id=
                                             self.profiles[self.profile][
                                                 'aws_access_key_id'],
                                             aws_secret_access_key=
                                             self.profiles[self.profile][
                                                 'aws_secret_access_key'],
                                             region_name=
                                             self.profiles[self.profile][
                                                 'region'],
                                             config=self._config)
                else:
                    endpoint = ('https://' if self.profiles[self.profile][
                        'https'] else 'http://') + \
                               self.profiles[self.profile]['endpoint']
                    if self.profiles[self.profile]['port']:
                        endpoint = '{}:{}'.format(endpoint,
                                                  self.profiles[self.profile][
                                                      'port'])
                    cl = self.session.client('s3',
                                             aws_access_key_id=
                                             self.profiles[self.profile][
                                                 'aws_access_key_id'],
                                             aws_secret_access_key=
                                             self.profiles[self.profile][
                                                 'aws_secret_access_key'],
                                             endpoint_url=endpoint,
                                             verify=False,
                                             config=self._config)
                    cl.meta.events.unregister('before-sign.s3',
                                              fix_s3_host)
            except Exception as e:
                _print('error: put -m failed...\nhint: {}'.format(e),
                       err=True)
                return

            # multipart upload wanted ?
            _mp_threshold = self.confitems.mpu_size if 'm' in para.flags else fsize + 1

            try:
                transconf = TransferConfig(multipart_threshold=_mp_threshold,
                                           max_concurrency=self.confitems.mpu_threads,
                                           multipart_chunksize=self.confitems.mpu_size,
                                           # we go with the defaults for the remainder
                                           # num_download_attempts=5,
                                           # max_io_queue=100,
                                           # io_chunksize=262144,
                                           # use_threads=True
                                           )
                transfer = S3Transfer(client=cl, config=transconf)

                if self.progress:
                    with click.progressbar(length=fsize, show_eta=True, show_percent=True, show_pos=True,
                                           label=f'PUT {".." + _src[-20:] if len(_src) > 22 else _src} ') as bar:
                        transfer.upload_file(_src, self.bucketname, _tgt,
                                             extra_args={'Metadata': _metadict, },
                                             callback=bar.update)
                else:
                    transfer.upload_file(_src, self.bucketname, _tgt,
                                         extra_args={'Metadata': _metadict,})
            except Exception as e:
                _print('error: transfer failed...\nhint: {}'.format(e),
                       err=True)
                return

    def do_quit(self, arg):
        'Exit hs3sh gracefully.'
        self.logger.info('--> called "quit {}"'.format(arg))

        _print('Ending gracefully...')
        return True

    def do_rm(self, arg):
        'rm object [version_id]\n' \
        '    Delete object (or it\'s version_id) from the attached bucket.'
        self.logger.info('--> called "rm {}"'.format(arg))

        if not self.profile:
            _print('error: you need to connect, first...', err=True)
            return

        if not arg:
            _print('error: at least one parameter is required...',
                  err=True)
            return

        if len(arg.split()) == 1:
            objct = arg
            # noinspection PyUnusedLocal
            version = None
            try:
                obj = self.s3.Object(self.bucketname, objct)
                response = obj.delete()
                _print('deleted "{}", version_id {}'
                      .format(objct,
                              response[
                                  'VersionId'] if 'VersionId' in response else 'null'))
            except Exception as e:
                _print('error: delete failed...\nhint: {}'.format(e),
                       err=True)
        else:
            try:
                objct, version = arg.split()
            except Exception as e:
                _print('error: one or two parameters are required...\nhint: {}'
                      .format(e), err=True)
            else:
                try:
                    obj = self.s3.Object(self.bucketname, objct)
                    response = obj.delete(VersionId=version)
                    _print('deleted "{}", version_id {}'
                          .format(objct,
                                  response[
                                      'VersionId'] if 'VersionId' in response else 'null'))
                except Exception as e:
                    _print('error: delete failed...\nhint: {}'.format(e),
                           err=True)

    def do_run(self, arg):
        'run <script>\n' \
        '    Run a batch of commands stored in file <script>.'
        try:
            para = hs3.parse.paramcheck(arg)
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   err=True)
            return
        else:
            if not len(para.args):
                _print('error: at least one parameter required...',
                       err=True)

        try:
            with open(para.args[0], 'r') as inhdl:
                for cmnd in inhdl.readlines():
                    cmnd = cmnd.strip()
                    # skip comments and empty lines
                    if cmnd and not cmnd.startswith('#'):
                        if cmnd.startswith('run'):
                            _print('skipping "{}"...'.format(cmnd))
                        else:
                            self.cmdqueue.append('_exec ' + cmnd.strip())
        except Exception as e:
            _print('error: running script "{}" failed...\nhint: {}'
                   .format(para.args[0], e), err=True)

    def do_set(self, args):
        'set config_item value\n' \
        '    known config items:\n' \
        '    mpu_size    : MultiPartUpload part size in MB\n' \
        '    mpu_threads : no. of concurrent uploads\n'
        self.logger.info('--> called "set {}"'.format(args))

        try:
            para = hs3.parse.paramcheck(args)
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   err=True)
            return
        else:
            if not len(para.args):
                # show actual config values
                for x in self.confitems.get:
                    _print(x)

            elif len(para.args) == 2:
                if para.args[0] in self.confitems.items:
                    try:
                        setattr(self.confitems, para.args[0],
                                1024**2*int(para.args[1]) if para.args[0] == 'mpu_size' else para.args[1])
                    except Exception as e:
                        _print('error: invalid parameters...\n\thint: {}'
                            .format(e))
                else:
                    _print('error: invalid config item: {}'.format(
                        para.args[0]))

            else :
                _print('error: exactly two parameters required...',
                       err=True)

    def do_status(self, arg):
        'status\n' \
        '    Show the session status (the connected endpoint and the\n' \
        '    attached bucket)'
        self.logger.info('--> called "status {}"'.format(arg))

        _print('{:>23} {}'.format('config item', 'value'))
        _print(f'{"-"*23} {"-"*55}')

        _print('{:>23} {}'.format('mode', self.mode or 'not set'))
        _print('{:>23} {}'.format('profile', self.profile or 'not set'))
        if self.profile:
            _print('{:>23}   {}'.format('profile comment',
                                      self.profiles[self.profile]['comment']))
            _print('{:>23}   {}'.format('session mode', 'secure (https)' if
                self.profiles[self.profile]['https'] else 'insecure (http)'))
            _print('{:>23}   {}'.format('endpoint',
                                      self.profiles[self.profile][
                                          'endpoint'] or 'Amazon S3'))
            _print('{:>23}   {}'.format('region',
                                      self.profiles[self.profile][
                                          'region'] or 'n/a'))
            _print('{:>23}   {}'.format('signature version',
                                      self.profiles[self.profile][
                                          'signature_version']))
            _print('{:>23}   {}'.format('payload signing enabled',
                                      str(self.profiles[self.profile][
                                          'payload_signing_enabled'])))
            _print('{:>23}   {}'.format('attached bucket',
                                        self.bucketname or 'not set'))
        _print()

    def do_time(self, arg):
        'time <command args>\n' \
        '    measure the time <command> takes to complete'
        self.logger.info('--> called "time {}"'.format(arg))

        p = arg.split(maxsplit=1)
        command, params = p if len(p) > 1 else (arg, '')

        st = time.time()
        if command:
            try:
                result = eval('self.do_{}("{}")'.format(command, params))
            except Exception as e:
                _print('error: time command failed...\n\thint: {}'.format(e),
                      err=True)
            else:
                # _print('[time: {}]'.format(calctime(time.time() - st)), err=True,
                #       flush=True)
                _print('[time: {}]'.format(calctime(time.time() - st)), err=True)
                return result
        else:
            _print('error: time command failed - no command given...',
                  err=True)

    def do_url(self, arg):
        'url [-e minutes] object\n' \
        '    Generate a pre-signed URL to access object\n' \
        '    -e set the expiration time for the URL to minutes\n' \
        '       (defaults to 60 minutes)\n' \
        '    -u generates an upload URL instead of a download URL'
        self.logger.info('--> called "url {}"'.format(arg))

        if not self.profile:
            _print('error: you need to connect, first...', err=True)
            return

        if not self.bucket:
            _print('error: you need to attach to a bucket, first...',
                  err=True)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='eu')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   err=True)
            return
        else:
            if 'e' in para.flags and len(para.args) != 2:
                _print('error: exactly 2 parameters are required...',
                      err=True)
                return
            elif 'e' not in para.flags and len(para.args) != 1:
                _print('error: exactly 1 parameter is required...',
                      err=True)
                return

            try:
                _expiresin = int(para.args[0]) if 'e' in para.flags else 3600
            except Exception as e:
                _print(
                    'error: expiration time is invalid...\nhint: {}'.format(e),
                    err=True)
                return
            _key = para.args[1] if 'e' in para.flags else para.args[0]

            try:
                if self.mode == 'aws':
                    cl = self.session.client('s3',
                                             aws_access_key_id=
                                             self.profiles[self.profile][
                                                 'aws_access_key_id'],
                                             aws_secret_access_key=
                                             self.profiles[self.profile][
                                                 'aws_secret_access_key'],
                                             region_name=
                                             self.profiles[self.profile][
                                                 'region'])
                else:
                    endpoint = ('https://' if self.profiles[self.profile][
                        'https'] else 'http://') + \
                               self.profiles[self.profile]['endpoint']
                    cl = self.session.client('s3',
                                             config=self._config,
                                             aws_access_key_id=
                                             self.profiles[self.profile][
                                                 'aws_access_key_id'],
                                             aws_secret_access_key=
                                             self.profiles[self.profile][
                                                 'aws_secret_access_key'],
                                             endpoint_url=endpoint)
                    # cl.meta.events.unregister('before-sign.s3', fix_s3_host)
            except Exception as e:
                _print('error: generation of pre-signed URL failed...\nhint: {}'
                       .format(e), err=True)
                return
            try:
                url = cl.generate_presigned_url('get_object' if not 'u' in para.flags else 'put_object',
                                                Params={
                                                    'Bucket': self.bucketname,
                                                    'Key': _key},
                                                ExpiresIn=_expiresin*60,
                                                HttpMethod=None)

                _print(url)
            except Exception as e:
                _print('error: generation of pre-signed URL failed...\nhint: {}'
                       .format(e), err=True)
                return

    def __mode(self, mode):
        '''
        From a st_mode Integer, calculate the ls-alike string

        :param mode:    a st_mode Integer
        :return:        a string
        '''
        self.logger.debug('--> called "__mode {}"'.format(mode))
        ret = 'd' if mode & S_IFDIR == S_IFDIR else '-'
        cnt = 0

        for i in str(bin(mode))[-9:]:
            # rwxr-xr-x
            if cnt in [0, 3, 6]:
                ret += 'r' if i == '1' else '-'
            elif cnt in [1, 4, 7]:
                ret += 'w' if i == '1' else '-'
            else:
                ret += 'x' if i == '1' else '-'
            cnt += 1

        return ret


    def __getcwd(self):
        """
        Secure version of os.getcwd that doesn't traceback in case the current
        working directory isn't accessible (maybe deleted underneath?)

        :return:    the cwd
        """
        try:
            return os.getcwd()
        except FileNotFoundError as e:
            return str(e)


def setdefaultattrs(obj, attrs):
    '''
     Sets the attributes in attr if they are not contained in obj.

    :param obj:     the object to check
    :param attrs:   a dict containing attributes to check as key and a default
                    value as value.
    :return:        a copy of the object containing the default values for
                    missing attributes
    '''

    for key in attrs.keys():
        if hasattr(obj, key):
            _print('obj {} has {} ({})'.format(obj, key, getattr(obj, key)))
        else:
            _print('obj {} doesn\'t have {} (default={})'.format(obj, key, attrs[key]))
            setattr(obj, key, attrs[key])
