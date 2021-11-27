# !/usr/bin/env python
# coding: utf-8

# !/usr/bin/env python
# coding: utf-8
import logging

from tronpytool import Tron

private = "44de82ce44f09f701e0b09f5773a0cc6823bf100b4e83552ba804388ab12db9d"
logger = logging.getLogger()

tron = Tron().setNetwork('nile')
tron.private_key = private
tron.getKey().printKeys()

# checked = validate_address(tron.getKey().address.sol)
