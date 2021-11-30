#
# Copyright 2020 Thomas Bastian, Jeffrey Goff, Albert Pang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

'''
#
# get_my_ip() returns the outgoing interface IP address of the local machine.
#
# Authors: Albert Pang
#
'''

'''
# Parameters
'''
'''
#
'''

import socket  # noqa: E402
try:
    # Python 3
    from urllib.request import urlopen
    IS_PYTHON3 = True
except ImportError:
    IS_PYTHON3 = False
    import urllib2

# An reachable external IP address to test out-going traffic
TEST_IP_ADDRESS = "8.8.8.8"

EXTERNAL_IP_CHECK_URLS = [
    "http://ipinfo.io/ip",
    "https://checkip.amazonaws.com",
    "http://myip.dnsomatic.com",
    "https://ident.me"
]


def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((TEST_IP_ADDRESS, 80))
    return s.getsockname()[0]

# https://stackoverflow.com/questions/2311510/getting-a-machines-external-ip-address-with-python


def get_my_external_ip3(url):
    return urlopen(url).read().decode('utf8').strip()


def get_my_external_ip2(url):
    req = urllib2.Request(url, data=None)
    response = urllib2.urlopen(req, timeout=5)

    return response.read().strip()


def get_my_external_ip():
    external_ip = "unknown"
    for url in EXTERNAL_IP_CHECK_URLS:
        try:
            if IS_PYTHON3:
                external_ip = get_my_external_ip3(url)
            else:
                external_ip = get_my_external_ip2(url)
            return external_ip
        except Exception:
            pass

    return external_ip


def main():
    print(get_my_ip())
    print(get_my_external_ip())


if __name__ == '__main__':
    main()
