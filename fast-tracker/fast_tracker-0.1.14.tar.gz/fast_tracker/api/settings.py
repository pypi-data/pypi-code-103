# -*- coding: utf-8 -*-
import fast_tracker.core.config

settings = fast_tracker.core.config.global_settings

RECORDSQL_OFF = 'off'
RECORDSQL_RAW = 'raw'
RECORDSQL_OBFUSCATED = 'obfuscated'

COMPRESSED_CONTENT_ENCODING_DEFLATE = 'deflate'
COMPRESSED_CONTENT_ENCODING_GZIP = 'gzip'

STRIP_EXCEPTION_MESSAGE = ("Message removed by FAST "
                           "'strip_exception_messages' setting")
