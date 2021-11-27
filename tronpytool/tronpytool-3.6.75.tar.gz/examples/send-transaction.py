#!/usr/bin/env python
# coding: utf-8
from tronpytool import Tron
from tronpytool import HttpProvider

tron = Tron().setNetwork('nile')
tron.private_key = 'private_key'
tron.default_address = 'default address'

# added message
send = tron.Chain.send_transaction('to', 1)

print(send)
