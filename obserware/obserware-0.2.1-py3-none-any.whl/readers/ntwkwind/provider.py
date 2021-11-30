"""
Obserware
Copyright (C) 2021 Akashdeep Dhar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import time

import psutil


def return_global_network_rate():
    pvntiocf = psutil.net_io_counters(pernic=False)
    time.sleep(1)
    nxntiocf = psutil.net_io_counters(pernic=False)
    globrate = {
        "rate_bytes_recv": (nxntiocf.bytes_recv - pvntiocf.bytes_recv) / 1024,
        "rate_bytes_sent": (nxntiocf.bytes_sent - pvntiocf.bytes_sent) / 1024,
        "rate_packets_recv": nxntiocf.packets_recv - pvntiocf.packets_recv,
        "rate_packets_sent": nxntiocf.packets_sent - pvntiocf.packets_sent,
    }
    retndata = {"globrate": globrate}
    return retndata


def return_pernic_threaded_statistics():
    pvntioct = psutil.net_io_counters(pernic=True)
    time.sleep(1)
    nxntioct = psutil.net_io_counters(pernic=True)
    tertdata, netifsat = (
        [],
        psutil.net_if_stats(),
    )
    for indx in nxntioct.keys():
        tertdata.append(
            (
                indx,
                netifsat[indx].isup,
                "%.2f KB/s"
                % float((nxntioct[indx].bytes_recv - pvntioct[indx].bytes_recv) / 1024),
                "%.2f KB/s"
                % float((nxntioct[indx].bytes_sent - pvntioct[indx].bytes_sent) / 1024),
                "%d packets/s"
                % int(nxntioct[indx].packets_recv - pvntioct[indx].packets_recv),
                "%d packets/s"
                % int(nxntioct[indx].packets_sent - pvntioct[indx].packets_sent),
                "%.2f KB" % float(int(nxntioct[indx].bytes_recv) / 1024),
                "%.2f KB" % float(int(nxntioct[indx].bytes_sent) / 1024),
                "%ld packets" % nxntioct[indx].packets_recv,
                "%ld packets" % nxntioct[indx].packets_sent,
                "%ld errors" % nxntioct[indx].errin,
                "%ld errors" % nxntioct[indx].errout,
                "%ld packets dropped" % nxntioct[indx].dropin,
                "%ld packets dropped" % nxntioct[indx].dropout,
                netifsat[indx].duplex.value,
                netifsat[indx].speed,
                netifsat[indx].mtu,
            )
        )
    retndata = {
        "niccount": len(nxntioct),
        "tertdata": tertdata,
    }
    return retndata


def return_mainscreen_threaded_statistics():
    netiocnf = psutil.net_io_counters(pernic=False)
    secodata = {
        "bytes_recv": netiocnf.bytes_recv,
        "bytes_sent": netiocnf.bytes_sent,
        "packets_recv": netiocnf.packets_recv,
        "packets_sent": netiocnf.packets_sent,
        "errin": netiocnf.errin,
        "errout": netiocnf.errout,
        "dropin": netiocnf.dropin,
        "dropout": netiocnf.dropout,
    }
    retndata = {
        "secodata": secodata,
    }
    return retndata
