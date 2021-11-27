#!/usr/bin/env python
# coding: utf-8
from tronpytool import Tron

tron = Tron().setNetwork('nile')

st1 = tron.address.to_hex('TT67rPNwgmpeimvHUMVzFfKsjL9GZ1wGw8')
st2 = tron.address.to_hex_0x('TT67rPNwgmpeimvHUMVzFfKsjL9GZ1wGw8')
st22 = tron.address.to_hex_0x_41('TT67rPNwgmpeimvHUMVzFfKsjL9GZ1wGw8')
st3 = tron.address.from_hex('41BBC8C05F1B09839E72DB044A6AA57E2A5D414A10')

print(st1)
# 41BBC8C05F1B09839E72DB044A6AA57E2A5D414A10
print(st2)
# 0xBBC8C05F1B09839E72DB044A6AA57E2A5D414A10
print(st22)
# 0x41BBC8C05F1B09839E72DB044A6AA57E2A5D414A10
print(st3)
# TT67rPNwgmpeimvHUMVzFfKsjL9GZ1wGw8
