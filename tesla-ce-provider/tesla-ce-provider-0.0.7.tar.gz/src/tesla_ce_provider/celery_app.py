#  Copyright (c) 2020 Xavier Baró
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" Celery client module """
import os
from celery import Celery
from kombu import Exchange, Queue
from tesla_ce_client import Client, exception

client = None
try:
    if os.getenv("SSL_VERIFY") in ['0', 0, 'False', 'false']:
        client = Client(verify_ssl=False)
    else:
        client = Client()
except exception.TeslaConfigException as tce:
    # Enforce valid configuration except when DEBUG is enabled
    if os.getenv('DEBUG', False) not in [1, '1', True, 'True', 'true']:
        raise tce


app = Celery('tesla_ce_provider')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
if client is not None:
    # Allow customize host and port
    custom_host = os.getenv('CELERY_BROKER_HOST', None)
    custom_port = os.getenv('CELERY_BROKER_PORT', None)
    if custom_host is not None:
        client.config['CELERY_BROKER_HOST'] = custom_host
    if custom_port is not None:
        client.config['CELERY_BROKER_PORT'] = custom_port

    app.config_from_object(client.config, namespace='CELERY')

# Get the queues to consume from
if client is not None and client.module:
    queues = client.module['provider_queue']
    queues = queues.replace(' ', '').split(',')

    # Create the Queues
    queue_list = tuple()
    with app.broker_connection() as connection:
        channel = connection.default_channel
        for queue in queues:
            queue_name = queue
            new_queue = Queue(queue_name,
                              exchange=Exchange(queue_name, type='direct', connection=connection),
                              routing_key=queue_name)
            new_queue(channel).declare()
            queue_list += (new_queue, )

    app.conf.task_queues = queue_list
