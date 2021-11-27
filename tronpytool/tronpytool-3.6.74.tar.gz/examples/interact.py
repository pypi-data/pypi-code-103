#!/usr/bin/env python
# coding: utf-8

from attrdict import AttrDict
from tronpytool.common import abi

from common.abi import method_result_handler
from tronpytool import Tron

tron = Tron().setNetwork('nile')
private_key = ''
wallet_address = ''
contract = 'TAgtKZmFtS8Mv94VVBKVFs72jjsCSJmXEi'
tron.private_key = private_key
tron.default_address = wallet_address
debug_health_contract = False
if debug_health_contract:
    collection = tron.Chain.get_contract(contract)
    print('Transaction: ')
    print(collection)
    print('-----------')

get_name_tx = tron.transaction_builder.trigger_smart_contract(data)

ok, constant_result, transaction_detail = method_result_handler(get_name_tx)

if ok:
    print("=======debug request result {}".format(constant_result[0]))
    res = constant_result[0]
    decodedbytes = bytes.fromhex(res)
    parse_res = abi.decode_single("", decodedbytes)
    print(parse_res)
    #   print(transaction_detail)
    print("=======end event report ========")
else:
    raise KeyError('Request returns Error - {} msg:{} txt:{}'.format(constant_result, transaction_detail, ""))
