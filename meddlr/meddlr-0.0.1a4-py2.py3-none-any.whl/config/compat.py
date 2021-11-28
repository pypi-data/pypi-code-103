"""
Backward compatibility of configs.

Instructions to bump version:
+ It's not needed to bump version if new keys are added.
  It's only needed when backward-incompatible changes happen
  (i.e., some existing keys disappear, or the meaning of a key changes)
+ To bump version, do the following:
    1. Increment _C.VERSION in defaults.py
    2. Add a converter in this file.

      Each ConverterVX has a function "upgrade" which in-place upgrades config
      from X-1 to X,
      and a function "downgrade" which in-place downgrades config from X to X-1

      In each function, VERSION is left unchanged.

      Each converter assumes that its input has the relevant keys
      (i.e., the input is not a partial config).
    3. Run the tests (test_config.py) to make sure the upgrade & downgrade
       functions are consistent.

Adapted from
https://github.com/facebookresearch/detectron2
"""

import logging
from typing import List, Optional, Tuple

from .config import CfgNode as CN
from .defaults import _C

__all__ = ["upgrade_config", "downgrade_config"]


def upgrade_config(cfg: CN, to_version: Optional[int] = None) -> CN:
    """
    Upgrade a config from its current version to a newer version.

    Args:
        cfg (CfgNode):
        to_version (int): defaults to the latest version.
    """
    cfg = cfg.clone()
    if to_version is None:
        to_version = _C.VERSION

    assert cfg.VERSION <= to_version, "Cannot upgrade from v{} to v{}!".format(
        cfg.VERSION, to_version
    )
    for k in range(cfg.VERSION, to_version):
        converter = globals()["ConverterV" + str(k + 1)]
        converter.upgrade(cfg)
        cfg.VERSION = k + 1
    return cfg


def downgrade_config(cfg: CN, to_version: int) -> CN:
    """
    Downgrade a config from its current version to an older version.

    Args:
        cfg (CfgNode):
        to_version (int):

    Note:
        A general downgrade of arbitrary configs is not always possible due to
        the different functionalities in different versions.
        The purpose of downgrade is only to recover the defaults in old
        versions, allowing it to load an old partial yaml config.
        Therefore, the implementation only needs to fill in the default values
        in the old version when a general downgrade is not possible.
    """
    cfg = cfg.clone()
    assert cfg.VERSION >= to_version, "Cannot downgrade from v{} to v{}!".format(
        cfg.VERSION, to_version
    )
    for k in range(cfg.VERSION, to_version, -1):
        converter = globals()["ConverterV" + str(k)]
        converter.downgrade(cfg)
        cfg.VERSION = k - 1
    return cfg


def guess_version(cfg: CN, filename: str) -> int:
    """
    Guess the version of a partial config where the VERSION field is not
    specified.
    Returns the version, or the latest if cannot make a guess.

    This makes it easier for users to migrate.
    """
    logger = logging.getLogger(__name__)

    def _has(name: str) -> bool:
        cur = cfg
        for n in name.split("."):
            if n not in cur:
                return False
            cur = cur[n]
        return True

    # Most users' partial configs have "MODEL.WEIGHT", so guess on it
    ret = None
    if _has("MODEL.WEIGHT") or _has("TEST.AUG_ON"):
        ret = 1

    if ret is not None:
        logger.warning("Config '{}' has no VERSION. Assuming it to be v{}.".format(filename, ret))
    else:
        ret = _C.VERSION
        logger.warning(
            "Config '{}' has no VERSION. "
            "Assuming it to be compatible with latest v{}.".format(filename, ret)
        )
    return ret


def _rename(cfg: CN, old: str, new: str) -> None:
    old_keys = old.split(".")
    new_keys = new.split(".")

    def _set(key_seq: List[str], val: str) -> None:
        cur = cfg
        for k in key_seq[:-1]:
            if k not in cur:
                cur[k] = CN()
            cur = cur[k]
        cur[key_seq[-1]] = val

    def _get(key_seq: List[str]) -> CN:
        cur = cfg
        for k in key_seq:
            cur = cur[k]
        return cur

    def _del(key_seq: List[str]) -> None:
        cur = cfg
        for k in key_seq[:-1]:
            cur = cur[k]
        del cur[key_seq[-1]]
        if len(cur) == 0 and len(key_seq) > 1:
            _del(key_seq[:-1])

    _set(new_keys, _get(old_keys))
    _del(old_keys)


class _RenameConverter:
    """
    A converter that handles simple rename.
    """

    RENAME: List[Tuple[str, str]] = []  # list of tuples of (old name, new name)

    @classmethod
    def upgrade(cls, cfg: CN) -> None:
        for old, new in cls.RENAME:
            _rename(cfg, old, new)

    @classmethod
    def downgrade(cls, cfg: CN) -> None:
        for old, new in cls.RENAME[::-1]:
            _rename(cfg, new, old)
