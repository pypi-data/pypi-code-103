#!/usr/bin/env python
#************************************************************************
# Copyright 2021 O7 Conseils inc (Philippe Gosselin)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#************************************************************************

"""Package to information from Pypi"""

import urllib.request
import json
import logging

#import pprint

logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class Pypi():
    """Class to explore Pypi"""

    #*************************************************
    #
    #*************************************************
    def __init__(self, project = 'o7cli'):

        self.project = project


    #*************************************************
    #
    #*************************************************
    def GetLatestVersion(self):
        """List all files in the current directory """
        url = f'https://pypi.org/pypi/{self.project}/json'
        try:
            data = json.load(urllib.request.urlopen(url=url))

        except Exception as error:
            logger.error(f'Failed to get latest version number ({error})')
            return None

        #pprint.pprint(data)

        version = data.get('info',{}).get('version',None)

        return version

#*************************************************
# To Test Class
#*************************************************
if __name__ == "__main__":


    thePypi = Pypi()
    theVersion = thePypi.GetLatestVersion()
    print(f'{theVersion=}')
