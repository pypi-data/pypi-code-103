import datetime
import io
import json

from google.cloud.exceptions import NotFound
from google.protobuf import timestamp_pb2
from google.cloud import pubsub_v1, storage
from google.cloud import tasks_v2


class PubSubService:
    """ Google Cloud PubSub Adapter"""

    __publisher = pubsub_v1.PublisherClient()

    def __init__(self, topic_id: str, access_token: str = None, project='expressmoney'):
        self.__topic_path = self.__publisher.topic_path(project, topic_id)
        self.__access_token = str(access_token)

    def publish(self, payload: dict = None):
        attrs = {'topic': self.__topic_path, }

        if payload and not isinstance(payload, dict):
            raise TypeError('Payload should be dict type')

        if payload:
            if self.__access_token:
                payload.update({'access_token': self.__access_token})
        else:
            if self.__access_token:
                payload = {'access_token': self.__access_token}
        if payload:
            attrs.update({'data': json.dumps(payload, ensure_ascii=False).encode('UTF-8')})

        self.__publisher.publish(**attrs)


class CloudTasksService:
    """ Google Cloud Tasks Adapter"""

    _client = tasks_v2.CloudTasksClient()

    def __init__(self,
                 access_token: str = None,
                 queue: str = 'attempts-1',
                 location: str = 'europe-west1',
                 project: str = 'expressmoney',
                 in_seconds: int = None,
                 ):
        """
        CloudTasks client
        Args:
            access_token: 'Bearer DFD4345345D'
            queue: 'my-appengine-queue'
            location: 'europe-west1'
            project: 'expressmoney'
            in_seconds: None
        """

        self._project = project
        self._in_seconds = in_seconds
        self._parent = self._client.queue_path(self._project, location, queue)
        self._uri = None
        self._payload = None
        self._update = False
        self._service = None
        self._access_token = access_token

    def run(self,
            service: str,
            uri: str,
            payload: dict = None,
            update: bool = False,
            ):
        """
        Start service execution
        Args:
            service: service name of App Engine
            uri: '/example_task_handler'
            payload: {'param': 'value'}
            update: True - PUT method
        """
        self._service = service
        self._uri = uri
        self._payload = payload
        self._update = update
        task = self._create_task()
        task = self._add_payload(task)
        task = self._convert_in_seconds(task)
        task = self._add_authorization(task)
        task = self._remove_empty_headers(task)
        self._client.create_task(parent=self._parent, task=task)

    def _create_task(self):
        task = {
            'app_engine_http_request': {
                'http_method': self._http_method,
                'relative_uri': self._uri,
                'headers': {},
                'app_engine_routing': {
                    'service': self._service,
                    'version': '',
                    'instance': '',
                    'host': '',

                }
            },
        }

        return task

    def _add_authorization(self, task):
        if self._access_token:
            task["app_engine_http_request"]["headers"]['Authorization'] = f'Bearer {self._access_token}'
        return task

    def _add_payload(self, task):
        if self._payload is not None:
            if not isinstance(self._payload, dict):
                raise TypeError('Payload should be dict type')
            payload = json.dumps(self._payload, ensure_ascii=False).encode('utf-8')
            task["app_engine_http_request"]["body"] = payload
            task["app_engine_http_request"]["headers"]['Content-Type'] = 'application/json'
        return task

    def _convert_in_seconds(self, task):
        if self._in_seconds is not None:
            d = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._in_seconds)
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(d)
            task['schedule_time'] = timestamp
        return task

    @staticmethod
    def _remove_empty_headers(task):
        if len(task['app_engine_http_request']['headers']) == 0:
            del task['app_engine_http_request']['headers']
        return task

    @property
    def _http_method(self):
        if self._update:
            return tasks_v2.HttpMethod.PUT
        else:
            return tasks_v2.HttpMethod.GET if self._payload is None else tasks_v2.HttpMethod.POST


class StorageService:
    """ Google Cloud Storage Adapter"""

    def __init__(self, bucket_name='expressmoney'):
        self._bucket_name = bucket_name
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(self._bucket_name)

    def upload_blob(self, source_file_name, destination_blob_name, type_file='pdf'):
        """Uploads a file to the bucket."""
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_string(source_file_name, content_type=f'application/{type_file}')

    def delete_blob(self, blob_name):
        """Deletes a blob from the bucket."""
        blob = self.bucket.blob(blob_name)
        blob.delete()

    def get_blob(self, path_to_file):
        """ Upload a file from the bucket. """
        blob = self.bucket.blob(path_to_file)
        try:
            file = io.BytesIO(blob.download_as_bytes())
            return file
        except NotFound:
            return None
