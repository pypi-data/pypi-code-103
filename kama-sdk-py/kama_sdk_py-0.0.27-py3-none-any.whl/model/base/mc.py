from typing_extensions import TypedDict

from kama_sdk.core.core import consts

"""
# TODO rename this module to model_consts once all `mc.*` BS is gone.
"""


NULLISH_ALIASES = ['__none__', '__null__', '__nil__', '__undefined__']
PREVENT_ALIASING_KEY = 'old'
SPLATTER_PREFIX = '...'
CACHE_SPEC_KEY = 'cache'
RE_DEFS_SPEC_KEY = 'redefine'
SPACE_KEY = 'space'
CONFIG_SPACE_KEY = 'config_space'

NEW_ATTR_PREFIX = "new__"
OLD_ATTR_PREFIX = "old__"
SUPPLIER_RESOLVE_PREFIX = "get::"
FORCE_INFLATE_PREFIX = "inflate::"
ID_REFERENCE_PREFIX = "id::"
EXPR_REFERENCE_PREFIX = "expr::"
KIND_REFERENCE_PREFIX = "kind::"
ASSETS_PREFIX = f'{consts.ASSETS_PREFIX}::'
LAZY_SYMBOL = "&"

ID_KEY = 'id'
TITLE_KEY = 'title'
SYNOPSIS_KEY = 'synopsis'
INHERIT_KEY = 'inherit'
KIND_KEY = 'kind'
INFO_KEY = 'info'
TAGS_KEY = 'tags'
LABELS_KEY = 'labels'

SEARCHABLE_LABEL = 'searchable'
STATUS_COMPUTER_LABEL = 'status_computer'

FULL_SEARCHABLE_KEY = f'{LABELS_KEY}.{SEARCHABLE_LABEL}'
FULL_STATUS_COMPUTER_KEY = f'{LABELS_KEY}.{STATUS_COMPUTER_LABEL}'

LAZY_KEY = 'lazy'
PATCH_KEY = 'patch'
WEAK_PATCH_KEY = 'weak_patch'

QUERY_KW = 'q'
ATTR_KW = 'attr'
KOD_KW = 'kod'
INFLATE_SAFELY_KW = 'safely'
BACKUP_KW = "backup"
DEPTH_KW = "depth"
LOOKUP_OPTIONS_KW = 'options'

SELF_LOOKUP_SUGAR = 'self'
PARENT_LOOKUP_SUGAR = 'parent'
NS_LOOKUP_KEY = 'ns'

DEFAULT_DEPTH = 0


STANDARD_READ_ENABLED_FLAG = 'standard'
REDEFINE_PREEMPT_ENABLED_FLAG = 'redefine'
VIRTUAL_PREEMPT_ENABLED_KEY = 'virtual'
CACHE_PREEMPT_ENABLED_FLAG = 'cache'
PARENT_LOOKBACK_ENABLED_FLAG = 'lookback'


class AttrLookupOpts(TypedDict, total=False):
  standard: bool
  redefine: bool
  virtual: bool
  cache: bool
  lookback: bool


PREVENT_REDEFINE_PREFIX = '_no_redefine_'
PREVENT_VIRTUAL_PREFIX = '_no_virtual_'
PREVENT_CACHE_PREFIX = '_no_cache_'
PREVENT_PARENT_PREFIX = '_no_lookback_'


DEF_LOOKUP_OPTS: AttrLookupOpts = {
  STANDARD_READ_ENABLED_FLAG: True,
  REDEFINE_PREEMPT_ENABLED_FLAG: True,
  VIRTUAL_PREEMPT_ENABLED_KEY: True,
  CACHE_PREEMPT_ENABLED_FLAG: True,
  PARENT_LOOKBACK_ENABLED_FLAG: True
}


LOOKUP_OPT_KEYS = DEF_LOOKUP_OPTS.keys()


prefix_sugar_sugar_mappings = [
  {
    'prefix': PREVENT_REDEFINE_PREFIX,
    'options': {REDEFINE_PREEMPT_ENABLED_FLAG: False}
  },
  {
    'prefix': PREVENT_CACHE_PREFIX,
    'options': {CACHE_PREEMPT_ENABLED_FLAG: False}
  },
  {
    'prefix': PREVENT_PARENT_PREFIX,
    'options': {PARENT_LOOKBACK_ENABLED_FLAG: False}
  },
  {
    'prefix': PREVENT_VIRTUAL_PREFIX,
    'options': {VIRTUAL_PREEMPT_ENABLED_KEY: False}
  }
]


class VirtualAttrEntry(TypedDict):
  func_name: str
  attr_name: str
  should_cache: bool
