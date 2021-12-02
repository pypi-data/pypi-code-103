__copyright__ = """
* Copyright (c) 2018 CA. All rights reserved.
*
* This software and all information contained therein is confidential and proprietary and
* shall not be duplicated, used, disclosed or disseminated in any way except as authorized
* by the applicable license agreement, without the express written permission of CA. All
* authorized reproductions must be marked with this language.
*
* EXCEPT AS SET FORTH IN THE APPLICABLE LICENSE AGREEMENT, TO THE EXTENT
* PERMITTED BY APPLICABLE LAW, CA PROVIDES THIS SOFTWARE WITHOUT WARRANTY
* OF ANY KIND, INCLUDING WITHOUT LIMITATION, ANY IMPLIED WARRANTIES OF
* MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT WILL CA BE
* LIABLE TO THE END USER OR ANY THIRD PARTY FOR ANY LOSS OR DAMAGE, DIRECT OR
* INDIRECT, FROM THE USE OF THIS SOFTWARE, INCLUDING WITHOUT LIMITATION, LOST
* PROFITS, BUSINESS INTERRUPTION, GOODWILL, OR LOST DATA, EVEN IF CA IS
* EXPRESSLY ADVISED OF SUCH LOSS OR DAMAGE.
"""
import logging
from ca_apm_agent.global_constants import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME[0] + '.instruments.import_hook')

_wily_import_orig__ = None
patch = None
patch_list = None
mod_set = set()
mod_len = len(mod_set)


def wily_import_hook(*args, **kwargs):
    if _wily_import_orig__ is not None:
        imported_module = _wily_import_orig__(*args, **kwargs)
        mod_set.add(imported_module)
        global mod_len
        if len(mod_set) != mod_len:
            mod_len = len(mod_set)
            logger.info('Module being loaded: %s', str(imported_module).strip('<>'))
            if imported_module.__name__ in patch_list:
                try:
                    if patch:
                        patch()
                    else:
                        logger.critical('Agent not started yet')
                except Exception as e:
                    logger.critical('FAILED TO INSTRUMENT :' + imported_module.__name__ + '\n' + str(e))
        return imported_module
    else:
        logger.debug('Import hook not initialized')
