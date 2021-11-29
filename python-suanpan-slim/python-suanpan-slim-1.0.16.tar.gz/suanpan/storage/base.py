# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import oss2
from minio import Minio
from suanpan.api import api
from suanpan.g import g
from suanpan.log import logger


class LocalStorage:
    def __init__(self, **kwds):
        pass

    def download(self, key, path):
        pass

    def upload(self, key, path):
        pass


class OssStorage:
    def __init__(self, **kwds):
        self.ossAccessId = g.get("storageOssAccessId")
        self.ossAccessKey = g.get("storageOssAccessKey")
        self.ossBucketName = g.get("storageOssBucketName")
        self.ossEndpoint = g.get("storageOssEndpoint")
        self.auth = None
        self.bucket = None

    def percentage(self, consumedBytes, totalBytes):
        if totalBytes:
            rate = int(100 * (float(consumedBytes) / float(totalBytes)))
            logger.info('\r{0}% '.format(rate))

    def refreshAccessKey(self):
        token = api.getOssToken()
        self.accessId = token["Credentials"]["AccessKeyId"]
        self.accessKey = token["Credentials"]["AccessKeySecret"]
        self.securityToken = token["Credentials"]["SecurityToken"]
        self.auth = oss2.StsAuth(self.accessId, self.accessKey,
                                 self.securityToken)
        self.bucket = oss2.Bucket(self.auth, self.ossEndpoint,
                                  self.ossBucketName)

    def download(self, key, path):
        if self.bucket:
            try:
                oss2.resumable_download(self.bucket,
                                        key,
                                        path,
                                        progress_callback=self.percentage)
            except:
                self.refreshAccessKey()
                oss2.resumable_download(self.bucket,
                                        key,
                                        path,
                                        progress_callback=self.percentage)
        else:
            self.refreshAccessKey()
            oss2.resumable_download(self.bucket,
                                    key,
                                    path,
                                    progress_callback=self.percentage)

    def upload(self, key, path):
        if self.bucket:
            try:
                oss2.resumable_upload(self.bucket,
                                      key,
                                      path,
                                      progress_callback=self.percentage)
            except:
                self.refreshAccessKey()
                oss2.resumable_upload(self.bucket,
                                      key,
                                      path,
                                      progress_callback=self.percentage)
        else:
            self.refreshAccessKey()
            oss2.resumable_download(self.bucket,
                                    key,
                                    path,
                                    progress_callback=self.percentage)


class MinioStorage:
    def __init__(self, **kwds):
        self.minioAccessKey = g.get("storageMinioAccessKey")
        self.minioSecretKey = g.get("storageMinioSecretKey")
        self.minioBucketName = g.get("storageMinioBucketName")
        self.minioEndpoint = g.get("storageMinioEndpoint")
        if self.minioEndpoint.startswith("https://"):
            self.endpoint = self.minioEndpoint.replace("https://", "")
            self.secure = True
        elif self.minioEndpoint.startswith("http://"):
            self.endpoint = self.minioEndpoint.replace("http://", "")
            self.secure = False
        self.client = Minio(
            self.endpoint,
            access_key=self.minioAccessKey,
            secret_key=self.minioSecretKey,
            secure=self.secure,
        )

    def download(self, key, path):
        self.client.fget_object(self.minioBucketName, key, path)

    def upload(self, key, path):
        self.client.fput_object(self.minioBucketName, key, path)


class Storage:
    def __init__(self):
        if g.get("storageType") == "oss":
            self.client = OssStorage()
        elif g.get("storageType") == "minio":
            self.client = MinioStorage()
        else:
            self.client = LocalStorage()

    def download(self, key, path):
        self.client.download(key, path)

    def upload(self, key, path):
        self.client.upload(key, path)

    def getPath(self, *path):
        return os.path.join(*path)

    def tmpOutputDataKey(self, requestId, port):
        return self.getPath("studio", g.userId, "tmp", g.appId, requestId,
                            g.nodeId, port)

    @property
    def configKey(self):
        return self.getPath("studio", g.userId, "configs", g.appId, g.nodeId)
