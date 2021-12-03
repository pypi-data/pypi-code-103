import boto3
import json
import logging
import uuid

logger = logging.getLogger('microgue')


class PublishFailed(Exception):
    pass


class AbstractResourceEventPublisher:
    stream_name = ''
    resource_id_field = 'id'

    def __init__(self):
        self.stream = boto3.client('kinesis')

    def publish_create(self, resource_after):
        return self._publish('create', {}, resource_after)

    def publish_update(self, resource_before, resource_after):
        return self._publish('update', resource_before, resource_after)

    def publish_delete(self, resource_before):
        return self._publish('delete', resource_before, {})

    def _publish(self, event_type, resource_before={}, resource_after={}):
        logger.debug("########## {} Publish ##########".format(self.__class__.__name__))
        logger.debug("event_type: {}".format(event_type))
        logger.debug("before: {}".format(resource_before))
        logger.debug("after: {}".format(resource_after))
        partition_key = resource_after.get(self.resource_id_field) if resource_after.get(self.resource_id_field, None) is not None else resource_before.get(self.resource_id_field)
        data = {
            'id': str(uuid.uuid4()),
            'event_type': '{}.{}'.format(self.stream_name, event_type),
            'before': resource_before,
            'after': resource_after
        }

        try:
            self.stream.put_record(
                StreamName=self.stream_name,
                PartitionKey=partition_key,
                Data=json.dumps(data)
            )
        except Exception as e:
            logger.error("########## {} Error".format(self.__class__.__name__))
            logger.error("{}: {}".format(e.__class__.__name__, str(e)))
            raise PublishFailed(str(e))

        return True
