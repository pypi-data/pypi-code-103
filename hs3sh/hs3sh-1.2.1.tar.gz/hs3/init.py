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


# initialized needed variables
#
class Gvars:
    """
    Holds constants and variables that need to be present within the
    whole project.
    """

    # version control
    s_version = "1.2.1"
    s_builddate = '2021-12-07'
    s_build = "{}/Sm".format(s_builddate)
    s_minPython = "3.7"
    s_description = "hs3sh"
    s_dependencies = ['boto3', 'click']

    # constants
    Version = "v.{} ({})".format(s_version, s_build)
    Description = 'HS3 shell - command processor for Amazon S3 and compatibles'
    Author = "Thorsten Simons"
    AuthorMail = "sw@snomis.eu"
    AuthorCorp = ""
    AppURL = ""
    License = "MIT"
    Executable = "hs3sh"


AWS_REGIONS = {'us-east-1': 'US East (N. Virginia)',
               'us-west-2': 'US West (Oregon)',
               'us-west-1': 'US West (N. California)',
               'eu-west-1': 'EU (Ireland)',
               'eu-central-1': 'EU (Frankfurt)',
               'ap-southeast-1': 'Asia Pacific (Singapore)',
               'ap-northeast-1': 'Asia Pacific (Tokyo)',
               'ap-southeast-2': 'Asia Pacific (Sydney)',
               'ap-northeast-2': 'Asia Pacific (Seoul)',
               'sa-east-1': 'South America (Sao Paulo)',
               }

TEMPLATE = ['# Configuration file used by hs3sh',
            '#',
            '# Profile for Amazon S3:',
            '# ----------------------',
            '# [aws]',
            '# type = aws',
            '# comment = <a comment>',
            '# region = eu-central-1',
            '# https = yes',
            '# port = 443',
            '# signature_version must be one of s3 or s3v4:',
            '# signature_version = s3v4',
            '# payload_signing_enabled = yes',
            '# aws_access_key_id = <your access key>',
            '# aws_secret_access_key = <your secret access key>',
            '',
            '# Profile for Cloudian HyperStore:',
            '# --------------------------------',
            '# [cloudian]',
            '# type = cloudian',
            '# comment = <a comment>',
            '# endpoint = s3-region.cloudian.your.domain',
            '# region = region',
            '# https = yes',
            '# port = 443',
            '# signature_version must be one of s3 or s3v4:',
            '# signature_version = s3v4',
            '# payload_signing_enabled = yes',
            '# aws_access_key_id = <your access key>',
            '# aws_secret_access_key = <your secret access key>',
            '',
            '# Profile for EMC ECS:',
            '# --------------------',
            '# [ecs]',
            '# type = ecs',
            '# comment = <a comment>',
            '# endpoint = namespace.ecs.your.domain',
            '# region = ',
            '# https = yes',
            '# port = 443',
            '# signature_version must be one of s3 or s3v4:',
            '# signature_version = s3v4',
            '# payload_signing_enabled = yes',
            '# aws_access_key_id = <your access key>',
            '# aws_secret_access_key = <your secret access key>',
            '',
            '# Profile for Hitachi Content Platform:',
            '# -------------------------------------',
            '# [hs3]',
            '# type = hs3',
            '# comment = <a comment>',
            '# endpoint = tenant.hcp.your.domain',
            '# region = ',
            '# https = yes',
            '# port = 443',
            '# signature_version must be one of s3 or s3v4:',
            '# signature_version = s3v4',
            '# payload_signing_enabled = yes',
            '# aws_access_key_id = <your access key>',
            '# aws_secret_access_key = <your secret access key>',
            '',
            '# Profile for other S3 compatible storage:',
            '# ----------------------------------------',
            '# [compatible]',
            '# type = compatible',
            '# comment = <a comment>',
            '# endpoint = whatever.your.domain',
            '# region = ',
            '# https = yes',
            '# port = 443',
            '# signature_version must be one of s3 or s3v4:',
            '# signature_version = s3v4',
            '# payload_signing_enabled = yes',
            '# aws_access_key_id = <your access key>',
            '# aws_secret_access_key = <your secret access key>',
            '',
            ]

INTRO = '\n'.join([' HS3 Shell v{} '.format(Gvars.s_version).center(79, '*'),
                   '',
                   'Type "help" for a list of available commands.'.center(79),
                   'Most commands support output redirection using "|", ">" '
                   'and ">>".'.center(79),
                   ''
                   ])

no_redir_cmds = ['attach', 'connect', 'quit']

AWSGROUPS = {'authenticateduser': 'http://acs.amazonaws.com/groups/global/AuthenticatedUsers',
             'allusers': 'http://acs.amazonaws.com/groups/global/AllUsers',
             'logdelivery': 'http://acs.amazonaws.com/groups/s3/LogDelivery',
             }
