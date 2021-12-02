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
import datetime
import re

# 3rd Party Modules
from typing import Optional

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.types as col_t

from scrapy.utils.project import get_project_settings
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint

# Project Modules
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from scrachy.db.base import Base


schema = get_project_settings().get('SCRACHY_SCHEMA')
schema = f'{schema}.' if schema else ''


class TimeStamp(sqlalchemy.types.TypeDecorator):
    # See: https://mike.depalatis.net/blog/sqlalchemy-timestamps.html
    @property
    def python_type(self):
        return datetime.datetime

    impl = sqlalchemy.types.TIMESTAMP
    LOCAL_TIMEZONE = datetime.datetime.utcnow().astimezone().tzinfo

    def process_literal_param(self, value, dialect):
        if value.tzinfo is None:
            value = value.astimezone(self.LOCAL_TIMEZONE)

        return value.astimezone(datetime.timezone.utc)

    def process_bind_param(self, value: datetime, dialect):
        if value.tzinfo is None:
            value = value.astimezone(self.LOCAL_TIMEZONE)

        return value.astimezone(datetime.timezone.utc)

    def process_result_value(self, value, dialect):
        if value.tzinfo is None:
            return value.replace(tzinfo=datetime.timezone.utc)

        return value.astimezone(datetime.timezone.utc)


# Some mixins
class AutoName(object):
    __table_args__ = {'schema': 'httpcache'} if schema else None

    # noinspection PyMethodParameters
    @declared_attr
    def __tablename__(cls):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()


class SettingOption(AutoName):
    # The name of the option.
    name = Column(col_t.Text, primary_key=True)

    # A unique integer identifying it.
    id = Column(col_t.SmallInteger, index=True, unique=True)


# Primary tables
class CacheRegion(Base, AutoName):
    # The name of the cache region
    name = Column(col_t.Text, primary_key=True)

    # The associated id
    id = Column(col_t.SmallInteger, index=True, unique=True)


class CacheRegionSettings(Base, AutoName):
    region_id = Column(
        col_t.SmallInteger,
        ForeignKey(f'{schema}cache_region.id'),
        primary_key=True
    )
    region = sqlalchemy.orm.relationship('CacheRegion')

    # The request fingerprint hashing algorithm used with this caching
    # region. All spiders using this region must use the exact same hashing
    # algorithm.
    fingerprint_hash_algorithm_id = Column(
        col_t.SmallInteger,
        ForeignKey(f'{schema}hash_algorithm.id'),
        nullable=False
    )
    fingerprint_hash_algorithm = sqlalchemy.orm.relationship('HashAlgorithm')


class CachedResponseBody(Base, AutoName):
    """
    Stores the minimum amount of information to recreate the html of a
    page given its request fingerprint. A new entry is added to this table
    every time the page is scraped regardless of whether the html has changed.
    """
    region_id = Column(col_t.SmallInteger, ForeignKey(f'{schema}cache_region.id'), primary_key=True)
    region = sqlalchemy.orm.relationship('CacheRegion')

    # The timestamp when the page was scraped.
    # scrape_timestamp = Column(col_t.TIMESTAMP(timezone=True), primary_key=True)
    scrape_timestamp = Column(TimeStamp(), primary_key=True)

    # A hash of the page's uniquely identifying request information.
    request_fingerprint = Column(col_t.LargeBinary, primary_key=True)

    # On the first scrape of the page this will be the full html text of the
    # response. On subsequent scrapes of the page it will either be a patch
    # string if the new response is different than the previous one, or it
    # will be null if it is the same.
    _response_body_html = Column('response_body_html', col_t.Text, nullable=True)

    # The settings associated with this region
    region_settings = sqlalchemy.orm.relationship(
        'CacheRegionSettings',
        viewonly=True,
        primaryjoin="CachedResponseBody.region_id==CacheRegionSettings.region_id",
        foreign_keys=region_id
    )

    @hybrid_property
    def response_body_html(self) -> str:
        return self._response_body_html or ''

    @response_body_html.setter
    def response_body_html(self, html: str):
        self._response_body_html = html


class CachedRequest(Base, AutoName):
    """
    Stores the request information corresponding to a page scraped at the given
    timestamp. Only requests that retrieve unique responses should be stored.
    """
    region_id = Column(
        col_t.SmallInteger,
        ForeignKey(f'{schema}cache_region.id'),
        primary_key=True
    )
    region = sqlalchemy.orm.relationship('CacheRegion')

    # The timestamp when the page was scraped.
    # scrape_timestamp = Column(col_t.TIMESTAMP(timezone=True), primary_key=True)
    scrape_timestamp = Column(TimeStamp(), primary_key=True)

    # A hash of the page's uniquely identifying request information.
    fingerprint = Column(col_t.LargeBinary, primary_key=True)

    # Request Details
    # The actual url
    url = Column(col_t.Text, index=True, nullable=False)

    # The net location of the url
    netloc = Column(col_t.Text, nullable=False)

    # The request method (True for GET. False for POST)
    _method = Column('method', col_t.Boolean, nullable=False)

    # The body of the request (primarily used for POST requests)
    body = Column(col_t.Text, nullable=True)

    ForeignKeyConstraint(
        ('region_id', 'scrape_timestamp', 'fingerprint'),
        (f'{schema}cached_response_body.region_id',
         f'{schema}cached_response_body.scrape_timestamp',
         f'{schema}cached_response_body.request_fingerprint')
    )

    @hybrid_property
    def method(self) -> Optional[str]:
        if self._method is True:
            return 'GET'
        elif self._method is False:
            return 'POST'

        return None

    # noinspection PyMethodParameters
    @method.expression
    def method(cls) -> Optional[str]:
        return sqlalchemy.case(
            [(cls._method == True, 'GET'),
             (cls._method == False, 'POST')],
            else_=None
        )

    @method.setter
    def method(self, method: str):
        self._method = method.upper() == 'GET'


class CachedResponseMeta(Base, AutoName):
    """
    Stores any additional metadata about the scraped page. A new entry in this
    table is only added when the response body has changed.
    """
    region_id = Column(
        col_t.SmallInteger,
        ForeignKey(f'{schema}cache_region.id'),
        primary_key=True
    )
    region = sqlalchemy.orm.relationship('CacheRegion')

    # The timestamp when the page was scraped.
    # scrape_timestamp = Column(col_t.TIMESTAMP(timezone=True), primary_key=True)
    scrape_timestamp = Column(TimeStamp(), primary_key=True)

    # A hash of the page's uniquely identifying request information.
    request_fingerprint = Column(col_t.LargeBinary, primary_key=True)

    # The response status code for the page
    response_status = Column(col_t.SmallInteger, index=True, nullable=True)

    # The response headers
    response_headers = Column(col_t.Text, nullable=False)

    # The method used to extract the body text.
    content_extraction_method_id = Column(
        col_t.SmallInteger,
        ForeignKey(f'{schema}content_extraction_method.id'),
        nullable=True
    )
    content_extraction_method = sqlalchemy.orm.relationship('ContentExtractionMethod')

    # The parser used to build the DOM
    content_extraction_parser_id = Column(
        col_t.SmallInteger,
        ForeignKey(f'{schema}html_parser.id'),
        nullable=True
    )
    content_extraction_parser = sqlalchemy.orm.relationship('HtmlParser')

    # The text of the response stripped of HTML and possibly stripped of
    # boilerplate content.
    # Note, unlike the html content, the full text is always stored (and not
    # the diff/patch).
    response_body_text = Column(col_t.Text, nullable=True)

    # The number of bytes of the full downloaded response (including the HTML)
    response_body_html_number_of_bytes = Column(col_t.Integer, nullable=False)

    # The number of bytes of the response excluding the HTML.
    response_body_text_number_of_bytes = Column(col_t.Integer, nullable=True)

    # The hashing algorithm used to produce the simhash
    simhash_hash_algorithm_id = Column(
        col_t.SmallInteger,
        ForeignKey(f'{schema}hash_algorithm.id'),
        nullable=True
    )
    simhash_hash_algorithm = sqlalchemy.orm.relationship('HashAlgorithm')

    # A simhash of the page's content excluding the HTML.
    # Note the value is computed as an unsigned 64bit integer, but it is stored
    # as a signed 64 bit integer because several of the database backends
    # do not support unsigned integer values. It can be converted back to an
    # unsigned value in python using
    # ctypes.c_ulonglong(response_body_text_simhash).value
    response_body_text_simhash = Column(col_t.BigInteger, nullable=True, index=True)

    ForeignKeyConstraint(
        ('region_id', 'scrape_timestamp', 'request_fingerprint'),
        (f'{schema}cached_response_body.region_id',
         f'{schema}cached_response_body.scrape_timestamp',
         f'{schema}cached_response_body.request_fingerprint')
    )


class HashAlgorithm(Base, SettingOption):
    def __repr__(self) -> str:
        # noinspection PyTypeChecker
        return self._repr(
            id=self.id,
            name=self.name
        )


class HtmlParser(Base, SettingOption):
    def __repr__(self) -> str:
        # noinspection PyTypeChecker
        return self._repr(
            id=self.id,
            name=self.name
        )


class ContentExtractionMethod(Base, SettingOption):
    def __repr__(self) -> str:
        # noinspection PyTypeChecker
        return self._repr(
            id=self.id,
            name=self.name
        )


class Tokenizer(Base, SettingOption):
    def __repr__(self) -> str:
        # noinspection PyTypeChecker
        return self._repr(
            id=self.id,
            name=self.name
        )
