#!/usr/bin/env python
# coding: utf-8
from tronpytool import Tron
from tronpytool import HttpProvider

tron = Tron().setNetwork('nile')


tron.toSun(1)
# result: 1000000

tron.fromSun(1000000)
# result: 1


