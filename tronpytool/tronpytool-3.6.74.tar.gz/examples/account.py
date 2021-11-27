#!/usr/bin/env python
# coding: utf-8
import logging
from tronpytool import Tron

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

private_key = 'da146374a75310b9666e834ee4ad0866d6f4035967bfc76217c5a495fff9f0d0'

tron = Tron().setNetwork("nile")


account = tron.create_account()
print(account.address)
is_valid = bool(tron.isAddress(account.address.hex))

logger.debug('Generated account: ')
logger.debug('- Private Key: ' + account.private_key)
logger.debug('- Public Key: ' + account.public_key)
logger.debug('- Address: ')
logger.debug('-- Base58: ' + account.address.base58)
logger.debug('-- Hex: ' + account.address.hex)
logger.debug('-- isValid: ' + str(is_valid))
logger.debug('-----------')
logger.debug('Test 2 set accounts')
tron.private_key = private_key
logger.debug('-----------')
