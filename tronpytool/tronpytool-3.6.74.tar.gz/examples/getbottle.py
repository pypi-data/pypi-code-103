#!/usr/bin/env python
# coding: utf-8
import logging

from tronpytool import Tron

# tron = Tron().setNetwork('nile')
tron = Tron().setNetwork('default')
hash_tx_id = "5bad50ba5b1fecab40f8685a808865872310e635be7f5eaa3aea77dc9da209ce"
dat = tron.Chain.get_transaction_note_confirmation(hash_tx_id)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

logger.debug('Transaction Result: ')
logger.debug(dat)
logger.debug('-----------')
