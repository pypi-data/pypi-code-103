#!/usr/bin/env python
# coding=utf-8

import os
import time
import subprocess

from afwfcfg.devbind import dev_get_info

afwf_cfg_filename = '/opt/afwf/config/afwf_core.cfg'


def do_cmd(cmd):
    return os.system(cmd)


def afwf_set_config(key, value, if_idx=-1):
    ret = -1
    filename = afwf_cfg_filename
    bk = filename+'.bk'
    do_cmd('mv %s %s' % (filename, bk))

    new_if_cfg = True

    new = ''
    with open(bk, 'r') as fp:
        for line in fp.read().split('\n'):
            if line == '':
                continue
            old_key = line.split()[0]
            if old_key == key:
                # global cfg
                if if_idx == -1:
                    new += (key + ' ' + value)
                # interface cfg
                else:
                    old_value = line.split()[1].split('-')
                    if if_idx == int(old_value[1]):
                        new += '%s if-%u-%s' % (key, if_idx, value)
                        new_if_cfg = False
                    else:
                        new += line
            else:
                new += line
            new += '\n'

        if new_if_cfg is True and if_idx != -1:
            new += '%s if-%u-%s\n' % (key, if_idx, value)
 
        new = new.rstrip('\n')
        ret = 0

    if ret == 0:
        ret = -1
        with open(filename, 'w') as fp:
            fp.write(new)
            ret = 0
    return ret


def afwf_del_config(key, if_idx=-1):
    ret = -1
    filename = afwf_cfg_filename
    bk = filename+'.bk'
    do_cmd('mv %s %s' % (filename, bk))

    new_if_cfg = True

    new = ''
    with open(bk, 'r') as fp:
        for line in fp.read().split('\n'):
            if line == '':
                continue
            old_key = line.split()[0]
            if old_key == key:
                # global cfg
                if if_idx == -1:
                    continue
                # interface cfg
                else:
                    old_value = line.split()[1].split('-')
                    if if_idx == int(old_value[1]):
                        continue
            else:
                new += line
            new += '\n'

        new = new.rstrip('\n')
        ret = 0

    if ret == 0:
        ret = -1
        with open(filename, 'w') as fp:
            fp.write(new)
            ret = 0

    return ret


def afwf_get_config(key, if_idx=-1):
    filename = afwf_cfg_filename
    with open(filename, 'r') as fp:
        for line in fp:
            config = line.split()
            if key == config[0]:
                # global cfg
                if if_idx == -1:
                    return config[1]
                # interface cfg
                else:
                    value = config[1].split('-')
                    if if_idx == int(value[1]):
                        return value[2]
    return ''


IF_DEV_IP = 'dev_ip'
REDIRECT_URL = 'redirect_url'
IF_DESIGNATED_MAC = 'designated_mac'
IF_DESIGNATED_MAC_DST = 'designated_mac_dst'
IF_DESIGNATED_MAC_SRC = 'designated_mac_src'
IF_INBOUND_VLAN_TAG = 'inbound_vlan_tag'
IF_OUTBOUND_VLAN_TAG = 'outbound_vlan_tag'
IF_PEER_PORT = 'peer_port'
IF_DPI_SWITCH = 'dpi'
IF_REDIRECT_SWITCH = 'redirect'


def save_bind_info(address):
    iRet = 0
    try:
        clear_bind_info(address)
        with open('/opt/afwf/config/bindinfo.cfg', 'a') as fp:
            fp.write('%s\n' % address)
    except Exception as e:
        print(e)
        iRet = -1
    return iRet


def clear_bind_info(address):
    filename = '/opt/afwf/config/bindinfo.cfg'
    bk = filename+'.bk'
    do_cmd('mv %s %s' % (filename, bk))

    new = ''
    with open(bk, 'r') as fp:
        for old_address in fp.read().split('\n'):
            if old_address == '':
                break
            if old_address != address:
                old_address.rstrip('\n')
                new += (old_address + '\n')
                
        if new != '':
            with open(filename, 'w') as fp:
                fp.write(new)
        else:
            os.system('touch %s' % filename)
    os.system('sudo rm %s' % bk)


def get_drv_from_devname(dev_name):
    if '82599' in dev_name:
        drv = 'ixgbe'
    elif '210' in dev_name:
        drv = 'igb'
    elif '82571' in dev_name:
        drv = 'e1000e'
    else:
        drv = None
    return drv


def bind_to_dpdk(address):
    # write cfg file
    save_bind_info(address)


def unbind_from_dpdk(address, dev_name):
    os.system('sudo initctl stop afwf')
    drv = get_drv_from_devname(dev_name)
    cmd_string = 'sudo opt/afwf/python/afwfcfg/devbind.py -u %s' % address
    do_cmd(cmd_string)
    clear_bind_info(address)

    if drv is not None:
        cmd_string = 'sudo /opt/afwf/python/afwfcfg/devbind.py --bind=%s %s' % (drv, address)
        do_cmd(cmd_string)
    else:
        print('unknow drv')
    os.system('sudo initctl start afwf')


def get_info():
    return dev_get_info()


def get_last_statistics(port_id):  
    try:
        (RX, TX) = (0, 0)
        with open('/opt/afwf/logs/afwf.log', 'r') as fp:
            laststa = subprocess.check_output(["grep port=%u /opt/afwf/logs/afwf.log | tail -1" % port_id],shell=True)
            if laststa != '':
                now = time.time()
                lasttime = float((laststa.split('<')[1]).split('>')[0])/1000
                if (now - lasttime) < 5:
                    RX = int(laststa.split()[4].split('RX=')[1])
                    TX = int(laststa.split()[7].split('TX=')[1])
        return RX, TX
    except Exception as e:
        print(e)
        return 0, 0


def set_mode_switch(switch):  
    try:
        aclRule = ('#priority action 		ethtype	l4port	l4proto tagethtype tagl4port   tagl4proto   tagvlanid tag-pppoe-code tag-pppoe-proto tag-pppoe-l4proto tag-pppoe-l4-dstport pppoe-code pppoe-proto pppoe-l4proto pppoe-l4-dstport',
                   '4 proc_icmp 0x0800 0 1 0 0 0 0 0 0 0 0 0 0 0 0',
                   '3 proc_udp_qry 0x0800 20000 17 0 0 0 0 0 0 0 0 0 0 0 0',
                   '2 proc_http 0x0800  80 6 0 0 0 0 0 0 0 0 0 0 0 0',
                   '1 proc_arp 0x0806 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
                   '5 proc_vlan_http 0x8100 0 0 0x0800 80 6 0 0 0 0 0 0 0 0 0',
                   '6 proc_vlan_pppoe_http 0x8100 0 0 0x8864 0 0 0 0x00 0x0021 6 80 0 0 0 0',
                   '7 proc_pppoe_http 0x8864 0 0 0 0 0 0 0 0 0 0 0x00 0x0021 6 80')
        os.system('mv /opt/afwf/config/ipv4_rules.cfg /opt/afwf/config/ipv4_rules.cfg.bak')
        with open('/opt/afwf/config/ipv4_rules.cfg', 'a') as fp:
            if switch == 0:
                fp.write(aclRule[0]+'\n')
                fp.write(aclRule[1]+'\n')
                fp.write(aclRule[2]+'\n')
                fp.write(aclRule[4])
            else:
                fp.write(aclRule[0]+'\n')
                fp.write(aclRule[3]+'\n')
                fp.write(aclRule[5]+'\n')
                fp.write(aclRule[6]+'\n')
                fp.write(aclRule[7])
    except Exception as e:
        os.system('mv /opt/afwf/config/ipv4_rules.cfg.bak /opt/afwf/config/ipv4_rules.cfg')
        return False
    os.system('rm /opt/afwf/config/ipv4_rules.cfg.bak')
    return True


def get_mode_switch():  
    try:
        mode = 1
        with open('/opt/afwf/config/ipv4_rules.cfg', 'r') as fp:
            for line in fp:
                if line.split()[0] == '4':
                    mode = 0
                    break
    except Exception as e:
        print(e)
        return -1
    return mode


def afwf_get_dpi_url():
    dpi_ip = afwf_get_config('dpi_ip')
    dpi_url_postfix = afwf_get_config('dpi_url_postfix')
    dpi_url = 'https://%s:5601/%s' % (dpi_ip, dpi_url_postfix)
    return dpi_url


if __name__ == '__main__':

    afwf_set_config(IF_DPI_SWITCH,'on',0)
    afwf_set_config(IF_REDIRECT_SWITCH,'on',0)
    print(afwf_get_config(IF_DPI_SWITCH,0))
    afwf_set_config(IF_REDIRECT_SWITCH,'on',0)
    print(afwf_get_config(IF_REDIRECT_SWITCH,0))
    # afwf_set_config(IF_PEER_PORT,'1',0)
    # print(afwf_get_config(IF_PEER_PORT, 1))
    # set_mode_switch(0)
    # print get_mode_switch()
    
    # bind_to_dpdk('66:00.0')
    # print get_last_statistics()
    # afwf_set_config(REDIRECT_URL, 'http://1.2.3.4/html?q=')
    # print afwf_get_config(REDIRECT_URL)
    '''i = 10
    while (i):
        save_bind_info('81:00.0')
        save_bind_info('02:00.0')
        afwf_set_config(IF_DEV_IP, '12.2.3.4', 0)
        afwf_set_config(IF_DEV_IP, '5.6.7.8', 1)
        afwf_set_config(REDIRECT_URL, 'http://1.2.3.4/html?q=')
        afwf_set_config(IF_DESIGNATED_MAC, 'on', 0)
        afwf_set_config(IF_DESIGNATED_MAC, 'off', 1)
        afwf_set_config(IF_DESIGNATED_MAC_DST, '00:00:00:00:00:01', 0)
        afwf_set_config(IF_DESIGNATED_MAC_DST, '00:00:00:00:00:02', 1)
        afwf_set_config(IF_DESIGNATED_MAC_SRC, '00:00:00:00:00:03', 0)
        afwf_set_config(IF_DESIGNATED_MAC_SRC, '00:00:00:00:00:04', 1)
        afwf_set_config(IF_INBOUND_VLAN_TAG, 'none', 0)
        afwf_set_config(IF_INBOUND_VLAN_TAG, 'dot1q', 1)
        afwf_set_config(IF_OUTBOUND_VLAN_TAG, 'keep', 0)
        afwf_set_config(IF_OUTBOUND_VLAN_TAG, 'strip', 1)
        print(afwf_get_config(IF_DEV_IP,0))
        print(afwf_get_config(REDIRECT_URL))
        print(afwf_get_config(IF_DESIGNATED_MAC,1))
        print(afwf_get_config(IF_DESIGNATED_MAC_DST, 0))
        print(afwf_get_config(IF_DESIGNATED_MAC_SRC, 1))

        linux_if, dpdk_if, other_if = get_info()
        print(linux_if)
        print(dpdk_if)
        print(other_if)

        bind_to_dpdk('81:00.0')
        unbind_from_dpdk('81:00.0', 'Intel Corporation-82599 10 Gigabit Network Connection')
        bind_to_dpdk('09:00.0')
        unbind_from_dpdk('09:00.0', 'Intel Corporation-I210 Gigabit Network Connection')
        i -= 1'''
