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
import os
import logging
import logging.config
from ca_apm_agent.global_constants import CA_APM_PYTHON_ACFG, ACFG_MTIME, PRINT_PREFIX, LOGGER_NAME
from ca_apm_agent.utils import network

logger = None


def read_instrument_cfg(cfg, fn):
    # Do not use logging here!
    from ca_apm_agent.patchers.constants import MODULE, CLASS, METHOD, PROBE_CLASS, PROBE_MODULE, PROBE_KEYS, PATCHED, LOADED

    ret_list = []
    probe_dict = {}
    patch_list = set()
    i = 1
    for line in cfg:
        if line.startswith('#') or line.startswith('\n'):
            i += 1
            continue
        line = line.replace(' ', '')

        if not line.startswith('('):
            try:
                key, values = line.split('=')
            except Exception as e:
                print (PRINT_PREFIX + fn + ':Something wrong in line ' + str(i) + '. Ignoring line and continuing')
                i += 1
                continue
            else:
                values = values.strip('()\r\n')
                v1, v2 = values.split(',')
                probe_dict[key] = {PROBE_MODULE: v1, PROBE_CLASS: v2, LOADED: False}

        else:
            line = line.strip('()\r\n')
            words = line.split(',')
            flag = False
            try:
                for key in words[3:]:
                    if key not in probe_dict:
                        print (PRINT_PREFIX + fn + 'Probe variable ' + key + ' not declared. Ignoring line ' + str(
                            i) + ' and continuing')
                        flag = True
                        break
                if flag:
                    i += 1
                    continue
                ret_list.append(
                    {MODULE: words[0],
                     CLASS: words[1],
                     METHOD: words[2],
                     PROBE_KEYS: words[3:],
                     PATCHED: False})
                patch_list.add(words[0])
            except:
                print (PRINT_PREFIX + fn + ':Something wrong in line ' + str(i) + '. Ignoring line and continuing')
                i += 1
                continue
        i += 1
    if ret_list:
        return ret_list, probe_dict, patch_list
    else:
        return None


def read_agent_cfg(cfg, fn):
    # Do not use logging here!
    import ast

    ret_dict = {}
    i = 1
    for line in cfg:
        t_dict = ret_dict
        if line.startswith('#') or line.startswith('\n'):
            i += 1
            continue
        try:
            keys, value_ = line.strip('\n').split('=', 1)
        except Exception as e:
            print (PRINT_PREFIX + fn + ':Something wrong in line ' + str(i) + '. Ignoring line and continuing')
            i += 1
            continue
        keylist = keys.split('.')
        for k in keylist[:-1]:
            if k not in t_dict:
                try:
                    t_dict[k] = {}
                except TypeError:
                    print (PRINT_PREFIX + fn + ':You are trying to nest a key ' + str(
                        keylist) + ' who has already been assigned a constant value')
                    return None
            t_dict = t_dict[k]
        try:
            t_dict[keylist[-1]] = ast.literal_eval(value_)
        except ValueError:
            t_dict[keylist[-1]] = value_
        except TypeError:
            print (PRINT_PREFIX + fn + ':You are trying to nest a key ' + str(
                keylist) + ' who has already been assigned a constant value')
            return None
        i += 1

    if ret_dict:
        return ret_dict
    else:
        return None


def configure_logger(cfg_dict, mpid):
    logging.config.dictConfig(cfg_dict)
    global logger
    logger = logging.getLogger(LOGGER_NAME[0] + '.config')
    # Changing log filename to include process id
    file_handler = None
    for x in logger.parent.handlers:
        if type(x).__name__ == 'RotatingFileHandler':
            file_handler = x
            break
    t = file_handler.baseFilename.split('.')
    if len(t) > 1:
        t.insert(-1, mpid)
        if os.path.exists(file_handler.baseFilename):
            # Initial file without PID being deleted
            os.remove(file_handler.baseFilename)
        file_handler.baseFilename = '.'.join(t)
    else:
        t.append(mpid)
        t.append('log')
        if os.path.exists(file_handler.baseFilename):
            # Initial file without PID being deleted
            os.remove(file_handler.baseFilename)
        file_handler.baseFilename = '.'.join(t)
    # Force a rollover so that the new logfile is created
    file_handler.doRollover()
    logger.debug('Logger configured and ready to work')


def agent_config_monitor(agent_object):
    import threading
    import os
    import time
    logger.debug('Attempting to start monitor')

    def aconfig_worker(agent_object):
        logger.info('Monitor started')
        while True:
            if agent_object.acfg_mtime != os.path.getmtime(os.environ[CA_APM_PYTHON_ACFG]):
                logger.info('Config file change detected')
                with open(os.environ[CA_APM_PYTHON_ACFG], 'r') as f:
                    cfg = f.readlines()
                cfg = read_agent_cfg(cfg, os.environ[CA_APM_PYTHON_ACFG])
                if cfg is None:
                    logger.warning('CFG file has some issues (check logs), please correct it')
                else:
                    cfg[ACFG_MTIME] = os.path.getmtime(os.environ[CA_APM_PYTHON_ACFG])
                    agent_object.apply_config(cfg)
                    processid = os.getpid()
                    containerid = network.getcontainerid()
                    
                    if containerid:
                       processid = containerid
                       
                    configure_logger(agent_object.log,str(processid))
                    logger.info('Changes applied')
            time.sleep(60)

    t = threading.Thread(name='agent_config_monitor', target=aconfig_worker, args=(agent_object,))
    t.daemon = True
    t.start()


def instrument_config_monitor():
    # TODO
    # Dynamic instrumentation in multi processing... phewwww  READ SIGHUP :D HAHAHAHA
    pass
