import base64
import os

import codefast as cf

URLBase64 = {
    'gost':
    b'aHR0cHM6Ly9maWxlZG4uY29tL2xDZHRwdjNzaVZ5YlZ5blBjZ1hnblBtL2dvc3QtbGludXgtYW1kNjQK'
}


class Piper:
    def get(self, app_name: str):
        url = base64.b64decode(URLBase64[app_name]).decode('utf-8').rstrip()
        cf.info('downloading [{}] from [{}]'.format(app_name, url))
        cf.net.download(url, os.path.join('/tmp/', app_name))

    def put(self, app_name: str, data: str):
        raise NotImplementedError


class PiperContext:
    pp = Piper()

    def run(self):
        for app_name in URLBase64:
            self.pp.get(app_name)
