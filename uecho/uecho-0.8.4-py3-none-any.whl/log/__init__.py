# Copyright (C) 2021 Satoshi Konno. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from .logger import setLevel, debug, info, warning, error
from .constants import DEBUG, INFO, WARNING, ERROR, CRITICAL, LOGGER_NAME

__all__ = ['setLevel', 'debug', 'info', 'warning', 'error', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'LOGGER_NAME']

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.NOTSET)
stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(stdout_handler)
