import os
import sys
from types import SimpleNamespace

if sys.version_info >= (3, 10, 0) or sys.version_info < (3, 8, 0):
    raise OSError(f'bert2tf requires Python 3.8/3.9, but yours is {sys.version}')

__proto_version__ = '0.0.22'

BERT2TF_GLOBAL = SimpleNamespace()
BERT2TF_GLOBAL.imported = SimpleNamespace()
BERT2TF_GLOBAL.imported.executors = False
BERT2TF_GLOBAL.imported.drivers = False

__bert2tf_env__ = (
    'BERT2TF_LOG_LONG',
    'BERT2TF_LOG_VERBOSITY',
    'BERT2TF_DEFAULT_HOST',
    'BERT2TF_PEA_NAME'
)

__default_host__ = os.environ.get('BERT2TF_DEFAULT_HOST', '0.0.0.0')
__stop_msg__ = 'terminated'
__ready_msg__ = 'ready for listening...'


def import_classes(namespace: str, targets=None, show_import_table: bool = False, import_once: bool = False):
    """
    Import all or selected executors into the runtime. This is called when bert2tf is first imported for registering the YAML
    constructor beforehand.

    :param namespace: the namespace to import
    :param targets: the list of executor names to import
    :param show_import_table: show the import result as a table
    :param import_once: import everything only once, to avoid repeated import
    """

    import os, sys, re
    from .logging import default_logger

    if namespace == 'bert2tf.executors':
        import_type = 'ExecutorType'
        if import_once and BERT2TF_GLOBAL.imported.executors:
            return
    elif namespace == 'bert2tf.drivers':
        import_type = 'DriverType'
        if import_once and BERT2TF_GLOBAL.imported.drivers:
            return
    else:
        raise TypeError(f'namespace: {namespace} is unrecognized')

    from setuptools import find_packages
    import pkgutil
    from pkgutil import iter_modules

    path = os.path.dirname(pkgutil.get_loader(namespace).path)

    modules = set()

    for info in iter_modules([path]):
        if not info.ispkg:
            modules.add('.'.join([namespace, info.name]))

    for pkg in find_packages(path):
        modules.add('.'.join([namespace, pkg]))
        pkgpath = path + '/' + pkg.replace('.', '/')
        if sys.version_info.major == 2 or (sys.version_info.major == 3 and sys.version_info.minor < 6):
            for _, name, ispkg in iter_modules([pkgpath]):
                if not ispkg:
                    modules.add('.'.join([namespace, pkg, name]))
        else:
            for info in iter_modules([pkgpath]):
                if not info.ispkg:
                    modules.add('.'.join([namespace, pkg, info.name]))

    # filter
    ignored_module_pattern = r'\.tests|\.api|\.bump_version'
    modules = {m for m in modules if not re.findall(ignored_module_pattern, m)}

    from collections import defaultdict
    load_stat = defaultdict(list)
    bad_imports = []

    if isinstance(targets, str):
        targets = {targets}
    elif isinstance(targets, list):
        targets = set(targets)
    elif targets is None:
        targets = {}
    else:
        raise TypeError(f'target must be a set, but received {targets!r}')

    depend_tree = {}
    import importlib
    from .helper import colored
    for m in modules:
        try:
            mod = importlib.import_module(m)
            for k in dir(mod):
                # import the class
                if (getattr(mod, k).__class__.__name__ == import_type) and (not targets or k in targets):
                    try:
                        _c = getattr(mod, k)
                        load_stat[m].append(
                            (k, True, colored('▸', 'green').join(f'{vvv.__name__}' for vvv in _c.mro()[:-1][::-1])))
                        d = depend_tree
                        for vvv in _c.mro()[:-1][::-1]:
                            if vvv.__name__ not in d:
                                d[vvv.__name__] = {}
                            d = d[vvv.__name__]
                        d['module'] = m
                        if k in targets:
                            targets.remove(k)
                            if not targets:
                                return  # target execs are all found and loaded, return
                    except Exception as ex:
                        load_stat[m].append((k, False, ex))
                        bad_imports.append('.'.join([m, k]))
                        if k in targets:
                            raise ex  # target class is found but not loaded, raise return
        except Exception as ex:
            load_stat[m].append(('', False, ex))
            bad_imports.append(m)

    if targets:
        raise ImportError(f'{targets} can not be found in bert2tf')

    if show_import_table:
        from .helper import print_load_table
        print_load_table(load_stat)
    else:
        if bad_imports:
            default_logger.warning(f'due to the missing dependencies or bad implementations, '
                                   f'{bad_imports} can not be imported ')

    if namespace == 'bert2tf.executors':
        BERT2TF_GLOBAL.imported.executors = True
    elif namespace == 'bert2tf.drivers':
        BERT2TF_GLOBAL.imported.drivers = True

    return depend_tree


import_classes('bert2tf.drivers', show_import_table=False, import_once=True)
import_classes('bert2tf.executors', show_import_table=False, import_once=True)

# add frequently-used imported
from .executors import BaseExecutor as Executor

from .executors.models import BaseModel as Model, PreTrainModel
from .executors.models.bert import Bert, BertPreTrainingModel
from .executors.models.roberta import Roberta, RobertaPreTraining
from .executors.models.electra import ElectraDiscriminator
from .executors.models.gpt import OpenAIGPT, OpenAIGPTPretraing, OpenAIGPTAutoRegressive, HuaweiGPT, \
    HuaweiGPTPreTraining, HuaweiGPTAutoRegressive
from .executors.models.plm_bert import PlmBert
from .executors.models.soft_masked_bert import SoftMaskedBert
from .executors.models.transformer import Transformer

from .executors.tokenizers.bert import BertTokenizer
from .executors.tokenizers.gpt import GPTTokenizer, HuaweiGPTTokenizer

from .executors.models.configs import BertConfig, ElectraConfig, GPTConfig, HuaweiGPTConfig, SoftMaskedBertConfig

from .flow import Flow



