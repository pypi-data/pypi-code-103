#
# Copyright (c) 2021, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
import logging
from sqlparse import format
from time import time

from django.conf import settings
from django.db import connection, reset_queries


def logging_queries(get_response):
    """
    Выводит в лог SQL-запросы на уровне DEBUG.
    """

    logger = logging.getLogger(__name__)
    REINDENT = getattr(settings, 'PRETTY_SQL_REINDENT', False)

    def pretty_sql(sql):
        return format(sql, reindent=REINDENT, keyword_case='upper')

    def middleware(request):
        if settings.DEBUG:
            reset_queries()
            start_queries = len(connection.queries)
            start_time = time()

            response = get_response(request)

            end_time = time()
            end_queries = len(connection.queries)

            queries = ''
            for i, query in enumerate(connection.queries):
                queries += (
                    f"\nQUERY #{i + 1}. {query['time']} seconds:\n"
                    f"{pretty_sql(query['sql'])}\n"
                )

            logger.debug(
                '%s %s -- %d database queries at %f seconds. %s',
                request.method,
                request.path,
                end_queries - start_queries,
                end_time - start_time,
                queries
            )
        else:
            response = get_response(request)

        return response

    return middleware
