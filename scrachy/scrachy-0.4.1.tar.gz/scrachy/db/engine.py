#  Copyright 2020 Reid Swanson.
#
#  This file is part of scrachy.
#
#  scrachy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  scrachy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with scrachy.  If not, see <https://www.gnu.org/licenses/>.

# Python Modules

# 3rd Party Modules
from contextlib import contextmanager
from typing import Type, List

import sqlalchemy as sqa
import sqlalchemy.orm

from scrapy.utils.project import get_project_settings
from sqlalchemy import event

# Project Modules
from scrachy.db.base import Base
from scrachy.utils.db import make_database_url
from scrachy.db.models import HashAlgorithm, HtmlParser, ContentExtractionMethod, Tokenizer
from scrachy.settings import VALID_HASH_ALGORITHMS, VALID_HTML_PARSERS, \
    VALID_CONTENT_EXTRACTION_METHODS, VALID_TOKENIZERS


schema = get_project_settings().get('SCRACHY_SCHEMA')
schema = f'{schema}.' if schema else ''


engine = sqa.create_engine(make_database_url(get_project_settings()))
session_factory = sqlalchemy.orm.sessionmaker(bind=engine)


@contextmanager
def session_scope():
    session = session_factory()

    if schema:
        session.execution_options = {
            "schema_translate_map": {"httpcache": schema}
        }

    # noinspection PyBroadException
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _insert_options(
        connection: sqlalchemy.engine.Connection,
        model_cls: Type,
        valid_options: List[str]
):
    session = sqlalchemy.orm.session.Session(bind=connection)

    if schema:
        session.execution_options = {
            "schema_translate_map": {"httpcache": schema}
        }

    # noinspection PyBroadException
    try:
        for i, name in enumerate(valid_options):
            session.add(model_cls(name=name, id=i))
        session.commit()
    except Exception:
        session.rollback()


# noinspection PyUnresolvedReferences,PyUnusedLocal
@event.listens_for(HashAlgorithm.__table__, 'after_create')
def _insert_hash_algorithms(target, connection, **kwargs):
    _insert_options(connection, HashAlgorithm, VALID_HASH_ALGORITHMS)


# noinspection PyUnresolvedReferences,PyUnusedLocal
@event.listens_for(HtmlParser.__table__, 'after_create')
def _insert_html_parsers(target, connection, **kwargs):
    _insert_options(connection, HtmlParser, VALID_HTML_PARSERS)


# noinspection PyUnresolvedReferences,PyUnusedLocal
@event.listens_for(ContentExtractionMethod.__table__, 'after_create')
def _insert_html_parsers(target, connection, **kwargs):
    _insert_options(connection, ContentExtractionMethod, VALID_CONTENT_EXTRACTION_METHODS)


# noinspection PyUnresolvedReferences,PyUnusedLocal
@event.listens_for(Tokenizer.__table__, 'after_create')
def _insert_html_parsers(target, connection, **kwargs):
    _insert_options(connection, Tokenizer, VALID_TOKENIZERS)


# This needs to be last
Base.metadata.create_all(engine)
