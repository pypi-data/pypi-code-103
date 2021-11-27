#!/usr/bin/env python
# coding: utf-8
import json
import logging

from tronpytool import Tron

tron = Tron().setNetwork('nile')
# tron = Tron().setNetwork('default')
# hash_tx_id = "5bad50ba5b1fecab40f8685a808865872310e635be7f5eaa3aea77dc9da209ce"
hash_tx_id = "61b37c3716df76b3dc92f765f42d2a2a0c2427c9a427ec99d566e4b21766b69e"
transaction = tron.Chain.get_transaction(hash_tx_id)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

logger.debug('Transaction: ')
logger.debug('- Hash: ' + transaction['txID'])
logger.debug('- Transaction: ' + json.dumps(transaction, indent=2))
logger.debug('-----------')

if "raw_data" in transaction:
    if "data" in transaction["raw_data"]:
        dat = transaction["raw_data"]["data"]
        decodedbytes = bytes.fromhex(dat)
        # parse_res = abi.decode_single("", decodedbytes)
        logger.debug(str(decodedbytes))
    if "contract" in transaction["raw_data"]:
        if len(transaction["raw_data"]["contract"]) > 0:
            dat = transaction["raw_data"]["contract"][0]
            if "parameter" in dat:
                if "value" in dat["parameter"]:
                    if "data" in dat["parameter"]["value"]:
                        hashdat = dat["parameter"]["value"]["data"]
                        fe = bytes.fromhex(hashdat)
                        logger.debug(str(fe))
                    if "owner_address" in dat["parameter"]["value"]:
                        hashdat = dat["parameter"]["value"]["owner_address"]
                        fe = tron.address.from_hex(hashdat)
                        logger.debug(str(fe))
    result = tron.Chain.get_transaction_info(hash_tx_id)
    # 111111331
    note = result["log"][0]["data"]

    # print(tron.address.from_hex(note))
    # print(note)
