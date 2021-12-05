import subprocess as sp
import time

import aria2p

from . import OS
from . import General
from . import Logger as Log


class Aria2:
    def __init__(self, host='0.0.0.0', port=6809, secret='1234', timeout=15):
        # %% create server
        a2c_bin = General.gen_os_exe_name('aria2c')
        if OS.is_windows():
            a2c_bin = f'{General.file_path(__file__)}/bin/{a2c_bin}'
            Log.info(f'{a2c_bin=}')
        self.server = sp.Popen(
            [a2c_bin, '--enable-rpc', f'--rpc-listen-port={port}',
             f'--rpc-secret={secret}'],
            stdin=sp.PIPE,
            stdout=sp.PIPE,
            stderr=sp.PIPE)
        Log.info(f'server started: {host=}, {port=}, secret=*****, {timeout=}...')
        # %%

        # %% wait for server to init
        r = ''
        while True:
            time.sleep(1)
            r += self.server.stdout.read(80).decode().lower()
            print(r)
            if r.find(f'listening on tcp port {port}') > -1:
                Log.info('server initialization completed...')
                break
            Log.info('waiting for server init...')
        # %%

        # %% then create client connection to rpc
        self.client = aria2p.API(
            aria2p.Client(host=f'http://127.0.0.1', port=port, secret=secret, timeout=timeout))
        self.client.set_global_options({'split': 8})

        Log.info(f'aria2p API client created: http://127.0.0.1:{port}, secret=*****, {timeout=}...')
        # %%

        self.host = host
        self.port = port
        self.secret = secret
        self.timeout = timeout

    def __del__(self):
        if self.server is not None:
            self.server.terminate()
            Log.info('server terminated.')

    def add_uris(self, uris: [str, list], _dir: str = None) -> aria2p.Download:
        if type(uris) is str:
            uris = [uris]

        if _dir is not None:
            _dir = {'dir': _dir}

        return self.client.add_uris(uris=uris, options=_dir)

    def download_file_sync(self, uris: [str, list], _dir: str = None):
        download = self.add_uris(uris, _dir)
        while not download.is_complete:
            time.sleep(.5)
            download.update()
            Log.info(f'{download.connections=}')
            Log.info(f'downloading: {download.progress_string()}')
        return download


'''aria2 = Aria2()
d = aria2.download_file_sync(uris='https://dl2.soft98.ir/soft/o/Opera.81.0.4196.60.x64.rar', _dir='d:/')

print(len(d.files))
for file in d.files:
    print(file.path)
'''
