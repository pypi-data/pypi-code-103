import logging
import os
import random
import re
import shutil
import string
import warnings

import bbcloud_python_sdk
import requests
from synology_api import filestation


class SynologyFileCache():

    def __init__(self, ip_address, port, username, password, cache_path_root, namespace=None):
        warnings.simplefilter('ignore', ResourceWarning)
        self.cache_path_root = cache_path_root
        self.namespace = namespace
        self.ip_address = ip_address
        self.port = port
        self.username = username
        self.password = password
        self.fl = None

    def getFl(self):
        if self.fl == None:
            self.fl = filestation.FileStation(ip_address=self.ip_address, port=self.port, username=self.username,
                                              password=self.password)
        return self.fl

    def random_str(self, num):
        salt = ''.join(random.sample(string.ascii_letters + string.digits, num))

        return salt

    def set_namespace(self, namespace):
        self.namespace = namespace
        return self

    def _exist(self, file_path):
        try:
            res = self.getFl().get_file_info(file_path)
            if res['data']['files'][0]['code'] == 408:
                return False
            elif res['data']['files'][0]['name']:
                return True
        except KeyError:
            return True

    def create_folder(self, folder_path):
        basename = os.path.basename(folder_path)
        dirname = os.path.dirname(folder_path)
        self.getFl().create_folder(folder_path=dirname, name=basename)

    def set(self, key, file_path, del_local=True):
        """
        缓存文件到群晖
        @param key: 缓存键
        @param file_path: 文件路径 url|本地目录|本地文件
        @param del_local: 缓存后是否删除本地文件
        """
        if not isinstance(file_path, str) and not isinstance(file_path, dict) and not isinstance(file_path, list) \
                and file_path is not None and not re.match("http", file_path) and not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        local_cache_path = '/tmp/%s.%s/%s' % (self.random_str(30), self.random_str(30), key)
        local_path = local_cache_path
        cache_path = "%s/%s" % (self.cache_path_root, self.namespace)

        if not self._exist(file_path=cache_path):
            self.create_folder(folder_path=cache_path)

        if not isinstance(file_path, list) and not isinstance(file_path, dict) and os.path.isfile(file_path):
            new_file_path = os.path.join(os.path.dirname(file_path), key)
            if file_path != new_file_path:
                shutil.copyfile(file_path, new_file_path)
            res = self.getFl().upload_file(dest_path=cache_path, file_path=new_file_path)

            if file_path != new_file_path:
                os.remove(new_file_path)

            if del_local:
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            if not os.path.exists(os.path.dirname(local_path)):
                bbcloud_python_sdk.make_dir(os.path.dirname(local_path))

            if isinstance(file_path, str) and re.match("http", file_path) and file_path is not None:
                bbcloud_python_sdk.download_file(file_path, local_path)
            elif isinstance(file_path, dict) or isinstance(file_path, list):
                bbcloud_python_sdk.create_json_file(local_path, file_path)
            elif os.path.isdir(file_path):
                bbcloud_python_sdk.zip_dirs(local_path, file_path)
            res = self.getFl().upload_file(dest_path=cache_path, file_path=local_path)

            logging.info(res)
            if del_local:
                if os.path.exists(local_path):
                    os.remove(local_path)

        if os.path.exists(local_cache_path):
            os.remove(local_cache_path)

        logging.info(res)
        return True

    def get(self, key, local_file):
        """
        从群晖获取缓存文件
        @param key: 缓存键
        @param local_file: 文本保存路径
        """
        cache_path = "%s/%s/%s" % (self.cache_path_root, self.namespace, key)
        local_file_dirname = os.path.dirname(local_file)

        try:
            self.getFl().get_file(path=cache_path, mode='download', dest_path=local_file_dirname)
            local_file_hash_name = os.path.join(local_file_dirname, key)
            if os.path.exists(local_file_hash_name):
                os.rename(local_file_hash_name, local_file)
                return True
            return False
        except requests.exceptions.HTTPError:
            return False

    def delete(self, key=None):
        """
        删除群晖缓存文件
        @param key:
        """
        cache_path = "%s/%s/%s" % (self.cache_path_root, self.namespace, key)

        if key is None:
            cache_path = "%s/%s" % (self.cache_path_root, self.namespace)

        try:
            return self.getFl().delete_blocking_function(path=cache_path).get('success', False)
        except:
            return False

    def exist(self, key):
        """
        判断缓存文件是否存在
        :param key:
        :return: True|False
        """
        file_path = "%s/%s/%s" % (self.cache_path_root, self.namespace, key)
        return self._exist(file_path=file_path)
