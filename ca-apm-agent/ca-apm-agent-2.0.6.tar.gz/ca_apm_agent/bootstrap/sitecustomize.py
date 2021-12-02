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
import sys
import builtins
from queue import Queue
import ca_apm_agent.config as config
from ca_apm_agent.global_constants import PRINT_PREFIX, LOGGER_NAME

environ = os.environ


def load_agent_config():
    from ca_apm_agent.global_constants import CA_APM_PYTHON_ACFG, ACFG_MTIME, CA_APM_PYTHON_HOST_NAME, CA_APM_PYTHON_PORT_NUM, CA_APM_PYTHON_APP_NAME
    flag = False
    cfg = None
    if CA_APM_PYTHON_ACFG in environ:
        try:
            # Loading config file
            cfg_file = open(environ[CA_APM_PYTHON_ACFG], 'r')
            cfg = cfg_file.readlines()
        except Exception as e:
            print (PRINT_PREFIX + 'Issues opening/reading provided agent config file, please check file and restart')
            print (str(e))
            print (PRINT_PREFIX + 'Using default agent config file')
            flag = True
        finally:
            cfg_file.close()
    else:
        flag = True

    if not flag:
        cfg = config.read_agent_cfg(cfg, environ[CA_APM_PYTHON_ACFG])
        if cfg is not None:
            cfg[ACFG_MTIME] = os.path.getmtime(environ[CA_APM_PYTHON_ACFG])
        else:
            print (PRINT_PREFIX + 'Provided Agent CFG file has some semantic issues - Please correct and restart')
            print (PRINT_PREFIX + 'Switching to default agent config file')
            flag = True

    if flag:
        import ca_apm_agent.directives as directives
        environ[CA_APM_PYTHON_ACFG] = os.path.join(os.path.dirname(os.path.realpath(directives.__file__)),
                                                   'agent.profile')
        try:
            cfg_file = open(environ[CA_APM_PYTHON_ACFG], 'r')
            cfg = cfg_file.readlines()
        except Exception as e:
            print (PRINT_PREFIX + 'Issues opening default agent config file. ' \
                                 'Possible corruption / incorrect installation of agent')
            print (str(e))
            print (PRINT_PREFIX + 'Will proceed without loading the agent')
            return None
        finally:
            cfg_file.close()
        cfg = config.read_agent_cfg(cfg, environ[CA_APM_PYTHON_ACFG])
        if cfg is not None:
            cfg[ACFG_MTIME] = os.path.getmtime(environ[CA_APM_PYTHON_ACFG])
        else:
            print (PRINT_PREFIX + 'Default Agent Config has semantic issues - Proceeding without loading the agent')

    if "CA_APM_PYTHON_HOST_NAME" in environ:
       cfg[CA_APM_PYTHON_HOST_NAME]=environ['CA_APM_PYTHON_HOST_NAME']
    else:
        if "ca_apm_python_host_name" in environ:
            cfg[CA_APM_PYTHON_HOST_NAME]=environ['ca_apm_python_host_name']

    if "CA_APM_PYTHON_PORT_NUM'" in environ:
       cfg[CA_APM_PYTHON_PORT_NUM]=environ['CA_APM_PYTHON_PORT_NUM']
    else:
        if "ca_apm_python_port_num" in environ:
            cfg[CA_APM_PYTHON_PORT_NUM]=environ['ca_apm_python_port_num']
 
    if "CA_APM_PYTHON_APP_NAME" in environ:
       cfg[CA_APM_PYTHON_APP_NAME]=environ['CA_APM_PYTHON_APP_NAME']
    else:
        if "ca_apm_python_app_name" in environ:
            cfg[CA_APM_PYTHON_APP_NAME]=environ['ca_apm_python_app_name']
    
    return cfg


def load_instrument_config():
    from ca_apm_agent.global_constants import CA_APM_PYTHON_ICFG, ICFG_MTIME
    flag = False
    cfg = None
    probe_dict = None
    patch_list = None
    if CA_APM_PYTHON_ICFG in environ:
        try:
            # Loading config file
            cfg_file = open(environ[CA_APM_PYTHON_ICFG], 'r')
            cfg = cfg_file.readlines()
        except Exception as e:
            print (PRINT_PREFIX + 'Issues opening/reading provided instrument config file, please check file and restart')
            print (str(e))
            print (PRINT_PREFIX + 'Using default agent config file')
            flag = True
        finally:
            cfg_file.close()
    else:
        flag = True

    if not flag:
        cfg, probe_dict, patch_list = config.read_instrument_cfg(cfg, environ[CA_APM_PYTHON_ICFG])
        if cfg is not None:
            cfg.append(os.path.getmtime(environ[CA_APM_PYTHON_ICFG]))
        else:
            print (PRINT_PREFIX + 'Provided Instrument CFG file has some semantic issues - Please correct and restart')
            print (PRINT_PREFIX + 'Switching to default agent config file')
            flag = True

    if flag:
        import ca_apm_agent.directives as directives
        environ[CA_APM_PYTHON_ICFG] = os.path.join(os.path.dirname(os.path.realpath(directives.__file__)),
                                                   'instrument.pbd')
        try:
            cfg_file = open(environ[CA_APM_PYTHON_ICFG], 'r')
            cfg = cfg_file.readlines()
        except Exception as e:
            print (PRINT_PREFIX + 'Issues opening default instrument config file. ' \
                                 'Possible corruption / incorrect installation of agent')
            print (str(e))
            print (PRINT_PREFIX + 'Will proceed without loading the agent')
            return None
        finally:
            cfg_file.close()
        cfg, probe_dict, patch_list = config.read_instrument_cfg(cfg, environ[CA_APM_PYTHON_ICFG])
        if cfg is not None:
            cfg.append(probe_dict)
            cfg.append(os.path.getmtime(environ[CA_APM_PYTHON_ICFG]))
        else:
            print (PRINT_PREFIX + 'Default Agent Config has semantic issues - Proceeding without loading the agent')

    return cfg, patch_list


if __name__ == 'sitecustomize':
    # Script starts here
    # Removing this file's path

    try:
        sys.path.remove(os.path.dirname(__file__))
    except ValueError:
        pass

    agent_cfg = load_agent_config()
    instrument_cfg, patch_list = load_instrument_config()
    LOGGER_NAME.extend(list(agent_cfg['log']['loggers']))  # list(dict) is a safe way to extract keys in py2&3

    if (agent_cfg is not None) and (instrument_cfg is not None):
        from ca_apm_agent.agent import Agent

        agent = Agent(agent_cfg, instrument_cfg, Queue(), Queue())

        import logging

        logger = logging.getLogger(LOGGER_NAME[0] + '.bootstrap.sitecustomize')

        try:
            agent.start_agent()
        except Exception as e:
            logger.error('Problems initializing agent')
            logger.debug('Problem encountered %s', str(e))
        else:
            # This import is critical and should be only done after the agent has started
            from ca_apm_agent.instruments import import_hook

            import_hook._wily_import_orig__ = builtins.__import__
            import_hook.patch = Agent.patch
            import_hook.patch_list = patch_list
            builtins.__import__ = import_hook.wily_import_hook
            logger.info('Import hook engaged')
        finally:
            pass

    logger.info('Attempting to remove injected sitecustomize')
    logger.debug('sys.modules %s', sys.modules)
    if sys.modules.pop('site', None) is not None:
        import logging
        import imp
        import sys
        from ca_apm_agent.global_constants import LOGGER_NAME

        logger = logging.getLogger(LOGGER_NAME[0] + '.bootstrap.sitecustomize')
        logger.info('Attempt Succeeded')
    else:
        logger.info('Attempt Failed - see debug logs')

    logger.debug('Attempting to load target app/environ sitecustomize')
    try:
        mod_data = imp.find_module('site')
        mod = imp.load_module('site', *mod_data)
        sys.modules['site'] = mod
        logger.debug('Attempt Succeeded')
    except ImportError:
        logger.warning('Unable to find target app/environ sitecustomize, if any')
    except Exception as e:
        logger.error('Exception in loading app/environ sitecustomize')
        logger.debug('Exception that was raised %s', str(e))
