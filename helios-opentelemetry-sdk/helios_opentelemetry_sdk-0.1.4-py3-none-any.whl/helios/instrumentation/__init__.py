from logging import getLogger

from helios.instrumentation.base import HeliosBaseInstrumentor
from helios.instrumentation.botocore import HeliosBotocoreInstrumentor
from helios.instrumentation.django import HeliosDjangoInstrumentor
from helios.instrumentation.elasticsearch import HeliosElasticsearchInstrumentor
from helios.instrumentation.fastapi import HeliosFastAPIInstrumentor
from helios.instrumentation.flask import HeliosFlaskInstrumentor
from helios.instrumentation.kafka import HeliosKafkaInstrumentor
from helios.instrumentation.requests import HeliosRequestsInstrumentor
from helios.instrumentation.urllib3 import HeliosUrllib3Instrumentor
from helios.instrumentation.redis import HeliosRedisInstrumentor

_LOG = getLogger(__name__)

instrumentor_names = [
    ('opentelemetry.instrumentation.boto', 'BotoInstrumentor'),
    ('opentelemetry.instrumentation.celery', 'CeleryInstrumentor'),
    ('opentelemetry.instrumentation.mysql', 'MySQLInstrumentor'),
    ('opentelemetry.instrumentation.pymongo', 'PymongoInstrumentor'),
    ('opentelemetry.instrumentation.pymysql', 'PyMySQLInstrumentor'),
    ('opentelemetry.instrumentation.sqlalchemy', 'SQLAlchemyInstrumentor'),
    ('opentelemetry.instrumentation.urllib', 'URLLibInstrumentor'),
]

default_instrumentation_list = [
    HeliosBotocoreInstrumentor(),
    HeliosDjangoInstrumentor(),
    HeliosElasticsearchInstrumentor(),
    HeliosFastAPIInstrumentor(),
    HeliosFlaskInstrumentor(),
    HeliosKafkaInstrumentor(),
    HeliosRedisInstrumentor(),
    HeliosRequestsInstrumentor(),
    HeliosUrllib3Instrumentor(),
]

for module_name, instrumentor_name in instrumentor_names:
    instrumentor = HeliosBaseInstrumentor.init_instrumentor(module_name, instrumentor_name)
    if instrumentor is not None:
        default_instrumentation_list.append(instrumentor)
