#!/usr/bin/env python
# -*- coding: utf-8 -*-


import boto3

from botocore.vendored.requests.packages.urllib3.exceptions import ResponseError
from botocore.exceptions import BotoCoreError, ClientError

from ..logging import logger
from ..message import sanitize_address
from .base import BaseEmailBackend


class SESEmailBackend(BaseEmailBackend):
    """
    Send mails using the AWS SES API.
    """

    def __init__(
        self,
        fail_silently=False,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_region_name=None,
        configuration_set_name=None,
        aws_region_endpoint=None,
        aws_config=None,
        ses_from_arn=None,
        ses_source_arn=None,
        ses_return_path_arn=None,
        **kwargs
    ):
        """Creates a client for the AWS SES API.

        :param fail_silently: If `True`, don't raise execeptions on client errors, defaults to False
        :type fail_silently: bool

        :param aws_access_key_id: the ``AWS_ACCESS_KEY_ID``, defaults to read from environment
        :type aws_access_key_id: str, optional

        :param aws_secret_access_key: the ``AWS_SECRET_ACCESS_KEY``, defaults to read from environment
        :type aws_secret_access_key: str, optional

        :param aws_region_name: the name of the AWS region to use, defaults to read from environment
        :type aws_region_name: str, optional

        :param configuration_set_name: the name of the SES Configuration Set to use, defaults to None
        :type configuration_set_name: str, optional

        :param aws_region_endpoint: the URL for the SES endpoint for the region, defaults to None
        :type aws_region_endpoint: str, optional

        :param aws_config: a properly constructed botocore Config object
        :type aws_config: class:`botocore.config.Config`, optional

        :param ses_from_arn: the FromArn when using cross-account identities, defaults to None
        :type ses_from_arn: str, optional

        :param ses_source_arn: the SourceArn when using cross-account identities, defaults to None
        :type ses_source_arn: str, optional

        :param ses_return_path_arn: the ReturnPathArn when using cross-account identities, defaults to None
        :type ses_return_path_arn: str, optional
        """
        super().__init__(fail_silently=fail_silently)
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region_name = aws_region_name
        self.aws_region_endpoint = aws_region_endpoint
        self.aws_config = aws_config
        self.ses_source_arn = ses_source_arn
        self.ses_from_arn = ses_from_arn
        self.ses_return_path_arn = ses_return_path_arn
        self.configuration_set_name = configuration_set_name

    def open(self):
        if self.connection:
            return False

        try:
            self.connection = boto3.client(
                "ses",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.aws_region_name,
                endpoint_url=self.aws_region_endpoint,
                config=self.aws_config
            )
        except (ClientError, BotoCoreError):
            if not self.fail_silently:
                raise
            return None
        return True

    def close(self):
        self.connection = None

    def send_messages(self, email_messages):
        """
        Sends one or more messages returns the number of email messages sent.

        :param email_messages: A list of emails to send
        :type email_messages: List[airmailer.message.EmailMessage]

        :raises: class:`botocore.exceptions.ClientError`: AWS SES had an issue
        :raises: class:`botocore.exceptions.BotoCoreError`: AWS SES had an issue

        :return: count of messages sent
        :rtype: int
        """
        if not email_messages:
            return 0

        new_conn_created = self.open()
        if not self.connection:
            return 0

        sent_message_count = 0

        for email_message in email_messages:
            if self._send(email_message):
                sent_message_count += 1

        if new_conn_created:
            self.close()

        return sent_message_count

    def _send(self, email_message):
        """
        Sends an individual message.

        If the message was submitted successfully to the AWS SES API, set

        * `email_message.extra_headers['status']` to 200
        * `email_message.extra_headers['message_id']` to the `MessageId`
        * `email_message.extra_headers['request_id']` to the `RequestId` of the AWS API call response

        If the message was not submitted successfully to the AWS SES API, set

        * `email_message.extra_headers['status']` to HTTP status of the response
        * `email_message.extra_headers['reason']` to "Reason" given for the error in the response
        * `email_message.extra_headers['error_code']` to error code of the response
        * `email_message.extra_headers['error_message']` to error message from the response
        * `email_message.extra_headers['body']` to body from the response
        * `email_message.extra_headers['request_id']` to the `RequestId` of the AWS API call response

        :param email_message: An email to send
        :type email_message: class:`airmailer.message.EmailMessage`

        :raises: class:`botocore.exceptions.ClientError`: AWS SES had an issue
        :raises: class:`botocore.exceptions.BotoCoreError`: AWS SES had an issue

        :return: True if the message was sent, False otherwise
        :rtype: bool
        """

        if not email_message.recipients():
            return False

        encoding = email_message.encoding
        from_email = sanitize_address(email_message.from_email, email_message.encoding)
        recipients = [sanitize_address(addr, encoding) for addr in email_message.recipients()]
        message = email_message.message()

        try:
            kwargs = {
                "Source": from_email,
                "Destinations": recipients,
                "RawMessage": {"Data": message.as_bytes(linesep="\r\n")},
            }

            if self.configuration_set_name is not None:
                kwargs["ConfigurationSetName"] = self.configuration_set_name
            if self.ses_source_arn:
                kwargs['SourceArn'] = self.ses_source_arn
            if self.ses_from_arn:
                kwargs['FromArn'] = self.ses_from_arn
            if self.ses_return_path_arn:
                kwargs['ReturnPathArn'] = self.ses_return_path_arn

            response = self.conn.send_raw_email(**kwargs)
        except ResponseError as err:
            # Store failure information so to post process it if required
            error_keys = ['status', 'reason', 'body', 'request_id',
                          'error_code', 'error_message']
            for key in error_keys:
                email_message.extra_headers[key] = getattr(err, key, None)
            if not self.fail_silently:
                raise
            if self.configuration_set_name:
                logger.debug(
                    "airmailer.ses.send.success from='{}' recipients='{}' request_id='{}' "
                    "ses-configuration-set='{}' status='{}' error_code='{}' error_message='{}'".format(
                        email_message.from_email,
                        ", ".join(email_message.recipients()),
                        email_message.extra_headers['request_id'],
                        self.configuration_set_name,
                        email_message.extra_headers['status'],
                        email_message.extra_headers['error_code'],
                        email_message.extra_headers['error_message'],
                    )
                )
            return False
        email_message.extra_headers['status'] = 200
        email_message.extra_headers['message_id'] = response['MessageId']
        email_message.extra_headers['request_id'] = response['ResponseMetadata']['RequestId']
        logger.debug(
            "airmailer.ses.send.success from='{}' recipients='{}' email_message_id='{}' request_id='{}' "
            "ses-configuration-set='{}'".format(
                email_message.from_email,
                ", ".join(email_message.recipients()),
                email_message.extra_headers['email_message_id'],
                email_message.extra_headers['request_id'],
                self.configuration_set_name
            )
        )
        return True
