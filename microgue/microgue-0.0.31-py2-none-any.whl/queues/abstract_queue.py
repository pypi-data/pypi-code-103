import boto3
import json
import logging

logger = logging.getLogger('microgue')


class QueueConnectionFailed(Exception):
    pass


class DeleteFailed(Exception):
    pass


class AbstractQueue:
    queue_url = ''

    def __init__(self, *args, **kwargs):
        try:
            self.queue = boto3.client('sqs')
        except Exception as e:
            raise QueueConnectionFailed(str(e))

    def send(self, message):
        logger.debug("########## {} Send ##########".format(self.__class__.__name__))
        if type(message) is dict:
            message = json.dumps(message)
        try:
            self.queue.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message
            )
        except Exception as e:
            logger.error("########## {} Send Failed".format(self.__class__.__name__))
            logger.error("{}: {}".format(e.__class__.__name__, str(e)))
            return False
        return True

    def receive(self, max_number_of_messages=1, visibility_timeout=1, wait_time=1):
        logger.debug("########## {} Receive ##########".format(self.__class__.__name__))
        logger.debug("max_number_of_messages: {}".format(max_number_of_messages))
        logger.debug("visibility_timeout: {}".format(visibility_timeout))
        logger.debug("wait_time: {}".format(wait_time))
        response = self.queue.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=max_number_of_messages,
            VisibilityTimeout=visibility_timeout,
            WaitTimeSeconds=wait_time
        )
        logger.debug("response: {}".format(response))
        response_messages = response.get('Messages', [])
        messages = []
        for i in range(len(response_messages)):
            try:
                message = {
                    'id': response_messages[i]['ReceiptHandle'],
                    'message': json.loads(response_messages[i]['Body'])
                }
                messages.append(message)
            except:
                pass
        return messages

    def delete(self, message):
        logger.debug("########## {} Delete ##########".format(self.__class__.__name__))
        logger.debug("message: {}".format(message))

        try:
            self.queue.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=message.get('id')
            )
        except Exception as e:
            logger.error("########## {} Delete Failed".format(self.__class__.__name__))
            logger.error("{}: {}".format(e.__class__.__name__, str(e)))
            raise DeleteFailed(str(e))

        return True
