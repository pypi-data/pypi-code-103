import logging
import os
import tarfile
import zipfile

import bbcloud_python_sdk as utils
from .ObsFileCache import ObsFileCache

from .OssFileCache import OssFileCache

from .SynologyFileCache import SynologyFileCache
from bbcloud_python_sdk.Api.Models.Artifacts import Artifacts


def runtime_logging(func):
    def wrap(*args, **kwargs):
        res = func(*args, **kwargs)
        logging.info(
            'FileCache:%s:%s:%s:%s' % (func.__name__, args[0].namespace, args if len(args) > 1 else kwargs, res))
        return res

    return wrap


class FileCache():
    def __init__(self, available_area, using_area):
        self.namespace = ''
        self.using_area = using_area
        self.available_area = available_area
        self.default_engine = self.getEngine(using_area=using_area)

    def getEngine(self, using_area=None):
        if not using_area:
            using_area = self.using_area
        engine = self.available_area[using_area]['engine']
        config = self.available_area[using_area]['config']
        if engine == 'OssFileCache':
            return OssFileCache(access_key_id=config['access_key_id'],
                                access_key_secret=config['access_key_secret'],
                                endpoint=config['endpoint'],
                                bucket_name=config['bucket_name'],
                                cache_path_root=config.get('cache_path_root', 'OssFileCache')
                                )
        elif engine == 'SynologyFileCache':
            return SynologyFileCache(
                ip_address=config['ip_address'],
                port=config['port'],
                username=config['username'],
                password=config['password'],
                cache_path_root=config.get('cache_path_root', 'SynologyFileCache')
            )
        elif engine == 'ObsFileCache':
            return ObsFileCache(
                access_key_id=config['access_key_id'],
                secret_access_key=config['access_key_secret'],
                endpoint=config['endpoint'],
                bucket_name=config['bucket_name'],
                cache_path_root=config.get('cache_path_root', 'ObsFileCache'))

    def set_namespace(self, namespace):
        self.namespace = namespace
        return self

    @runtime_logging
    def set(self, key, file_path, del_local=True, set_all_area=False, artifacts_config=None):
        if set_all_area:
            is_set = self.default_engine.set_namespace(namespace=self.namespace).set(key=key, file_path=file_path,
                                                                                     del_local=False)
            if is_set and artifacts_config is not None:
                self.create_artifacts(
                    key=key,
                    namespace=self.namespace,
                    name=artifacts_config.get('name'),
                    engine=self.default_engine.__class__.__name__,
                    describe=artifacts_config.get('describe'),
                    jenkins_jobs_id=artifacts_config.get('jenkins_jobs_id'),
                    build_id=artifacts_config.get('build_id'),
                    ttl=artifacts_config.get('ttl'),
                    is_scan_code_download=artifacts_config.get('is_scan_code_download')
                )

            for area in self.available_area:
                if area is not self.using_area:
                    engine = self.getEngine(using_area=area)
                    is_set = engine.set_namespace(namespace=self.namespace).set(key=key, file_path=file_path,
                                                                                del_local=False)
                    if is_set and artifacts_config is not None:
                        self.create_artifacts(
                            key=key,
                            namespace=self.namespace,
                            name=artifacts_config.get('name'),
                            engine=engine.__class__.__name__,
                            describe=artifacts_config.get('describe'),
                            jenkins_jobs_id=artifacts_config.get('jenkins_jobs_id'),
                            build_id=artifacts_config.get('build_id'),
                            ttl=artifacts_config.get('ttl'),
                            is_scan_code_download=artifacts_config.get('is_scan_code_download')
                        )
        else:
            is_set = self.default_engine.set_namespace(namespace=self.namespace).set(key=key, file_path=file_path,
                                                                                     del_local=del_local)
            if is_set and artifacts_config is not None:
                self.create_artifacts(
                    key=key,
                    namespace=self.namespace,
                    name=artifacts_config.get('name'),
                    engine=self.default_engine.__class__.__name__,
                    describe=artifacts_config.get('describe'),
                    jenkins_jobs_id=artifacts_config.get('jenkins_jobs_id'),
                    build_id=artifacts_config.get('build_id'),
                    ttl=artifacts_config.get('ttl'),
                    is_scan_code_download=artifacts_config.get('is_scan_code_download')
                )

        return is_set

    def create_artifacts(self, key, namespace, engine, name=None, describe=None, jenkins_jobs_id=None, build_id=None,
                         ttl=None,
                         is_scan_code_download=False):
        path = "%s/%s" % (namespace, key)
        try:
            Artifacts().updateOrCreate(
                {
                    'path': path,
                    'engine': engine,
                },
                {
                    'name': key if name is None else name,
                    'describe': describe,
                    'path': path,
                    'engine': engine,
                    'jenkins_jobs_id': jenkins_jobs_id,
                    'build_id': build_id,
                    'ttl': 1296000 if ttl is None else ttl,
                    'is_scan_code_download': 1 if is_scan_code_download else 0,
                }
            )
        except Exception as e:
            logging.info('制品创建失败:%s' % e)

    @runtime_logging
    def get(self, key, local_file, default=None, auto_unzip=False, auto_delete_local_zip=True, auto_untar=False,
            auto_delete_local_tar=True, retry=1):
        """
        :param key: 文件缓存key
        :param local_file: 本地保存路径
        :param default: 如果没有获取到文件缓存，则使用默认替代资源地址，替代资源如果获取成功会被存到文件缓存系统
        :param auto_unzip:如果是zip类型文件缓存，是否自动解压缩
        :param auto_delete_local_zip:zip自动解压缩后是否删除压缩包
        :param auto_untar:如果是tar类型文件缓存，是否自动解压缩
        :param auto_delete_local_tar:tar自动解压缩后是否删除压缩包
        :param retry:重试次数，默认为1，获取数据异常时使用，一般不修改
        :return:
        """
        if retry >= 0:
            if not os.path.exists(os.path.dirname(local_file)):
                utils.make_dir(os.path.dirname(local_file))

            is_get = self.default_engine.set_namespace(namespace=self.namespace).get(key=key, local_file=local_file)
            if not is_get:
                if default:
                    self.set(key=key, file_path=default, del_local=True)
                    is_get = self.get(key=key, local_file=local_file)
                else:
                    return False

            if is_get:
                if auto_unzip or auto_untar:
                    is_unpack = self.unpack(local_file=local_file)
                    if not is_unpack:
                        os.remove(local_file)
                        return self.get(
                            key=key,
                            local_file=local_file,
                            default=default,
                            auto_unzip=auto_unzip,
                            auto_delete_local_zip=auto_delete_local_zip,
                            auto_untar=auto_untar,
                            auto_delete_local_tar=auto_delete_local_tar,
                            retry=retry - 1
                        )
                    if auto_delete_local_zip or auto_delete_local_tar:
                        os.remove(local_file)
                return True
            else:
                return False
        else:
            return False

    def unpack(self, local_file):
        if os.path.splitext(local_file)[-1] == '.zip':
            unzip_dir = os.path.dirname(local_file)
            if os.path.exists(local_file):
                if zipfile.is_zipfile(local_file):
                    utils.unzip(file_name=local_file, dst_dir=unzip_dir)
                    return True

        elif os.path.splitext(local_file)[-1] == '.gz':
            untar_dir = os.path.dirname(local_file)
            if os.path.exists(local_file):
                if tarfile.is_tarfile(local_file):
                    utils.untar(file_name=local_file, dst_dir=untar_dir)
                    return True

        logging.info('解压失败，请检查压缩文件格式：%s' % local_file)

        return False

    @runtime_logging
    def delete(self, key=None, delete_all_area=False):
        if delete_all_area:
            self.default_engine.set_namespace(namespace=self.namespace).delete(key=key)

            for area in self.available_area:
                if area is not self.using_area:
                    self.getEngine(using_area=area).set_namespace(namespace=self.namespace).delete(key=key)
            return True
        else:
            return self.default_engine.set_namespace(namespace=self.namespace).delete(key=key)

    @runtime_logging
    def exist(self, key):
        return self.default_engine.set_namespace(namespace=self.namespace).exist(key=key)

    @runtime_logging
    def list_cache_objects(self):
        return self.default_engine.set_namespace(namespace=self.namespace).list_cache_objects()

    @runtime_logging
    def list_dir(self, deep_num):
        return self.default_engine.set_namespace(namespace=self.namespace).list_dir(deep_num=deep_num)
