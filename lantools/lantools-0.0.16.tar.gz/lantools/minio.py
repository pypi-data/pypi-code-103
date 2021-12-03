from minio import Minio

class PyMinio:
    def __init__(self, host, port, access_key, secret_key, secure=False):
        self.client = Minio(
            "{}:{}".format(host, port),
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )

    def set_bucket(self, bucket):
        self.bucket = bucket

    def download(self, object_name:str, local_name:str) -> bool:
        self.client.fget_object(self.bucket, object_name, local_name)
        return True

    def upload(self, file_path:str, object_name:str) -> bool:
        if self.client.bucket_exists(self.bucket) == False:
            self.client.make_bucket(self.bucket)  # 生成一个bucket，类似文件夹

        self.client.fput_object(
            bucket_name=self.bucket,
            object_name=object_name,
            file_path=file_path
        )
        return True

    def exists(self, object_name:str) -> bool:
        try:
            response = self.client.get_object(self.bucket, object_name)
            response.close()
            response.release_conn()
            return True
        except Exception as e:
            return False

    # 删除对象
    def remove_file(self, object_name:str) -> bool:
        try:
            self.client.remove_object(self.bucket, object_name)
            print("Sussess")
            return True
        except Exception as err:
            print(err)
            return False

    def get_client(self) -> Minio:
        return self.client
