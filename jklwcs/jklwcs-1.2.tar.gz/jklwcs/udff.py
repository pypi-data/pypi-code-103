# -*- coding: utf-8 -*-
'''
@File  : udff.py
@Author: Jike Data Analysis Modeling Group
@Date  : 2021/12/4 12:13 上午
@Desc  : 自定义udf函数
'''

from pyspark.sql.functions import udf

@udf
def get_package_name(app_id):
    # app_id与渠道映射关系
    PACKAGE_MAPPING = {
        "mx-geek": "com.sharedream.geek.demo",
        "meizu": "com.meizu.assistant",
        "cmsyx": "com.chinamobile.cmccwifi",
        "asus": "com.asus.launcher3",
        "gionee": "com.gionee.amisystem.yourpage",
        "gome": "com.gome.launcher",
        "nubia": "cn.nubia.edge",
        "nubia-app": "cn.nubia.edge.app",
        "nubia-test": "cn.nubia.edge.test",
        "phicomm": "com.phicomm.zeroscreen",
        "hmct": "com.hmct.intelligent",
        "fanzhuo": "com.android.fanzhuo.geek",
        "plugin": "com.sharedream.wlan.sdk.plugin",
        "ipip": "",
        "mx-test": "",
        "ebensz": "com.ebensz.thirdpartner",
        "wingos": "com.wingos.smartscene",
        "mydream": "com.mydream.wifi",
        "wifi": "com.wifi.key",
        "nokia": "com.android.nokia",
        "ivvi": "com.ivvi.moassistant",
        "siui": "com.siui.android.launcher",
        "xtc": "com.xtc.test.location",
        "gree": "com.android.gree",
        "mx-all": "com.sharedream.geek.app.all",
        "mx-selected": "com.sharedream.geek.app.selected",
        "smartisanos": "com.smartisanos.launcher",
        "zte": "com.zte.mifavor.miboard",
        "vivodemo": "com.sharedream.geek.demo.vivo",
        "vivo": "com.vivo.assistant",
        "sugarmyos": "com.myos.leftpage",
        "samsung": "com.samsung.android.app.sreminder",
        "oppodemo": "com.sharedream.geek.demo.oppo",
        "huaweidemo": "com.sharedream.geek.demo.huawei",
        "oppo": "com.coloros.sceneservice",
        "cmic": "com.cmic.customcontent",
        "huawei": "com.huawei.intelligent",
        "vivoai": "com.vivo.aiengine",
        "vivonew": "com.vivo.assistant.new",
        "oneplus": "com.sharedream.geek.demo.oneplus",
        "miui": "com.miui.hybrid.o2o",
        "lwx": "com.lwx.location.app",
        "miuios": "com.miui.hybrid.accessory",
        "hwapp": "com.huawei.quickapp.plugin",
        "nubiaapp": "cn.nubia.edge.quickapp",
        "okii": "com.sharedream.geek.demo.okii",
        "hwlocation": "com.huawei.imax.dolphin.location",
        "vivoapc": "com.vivo.allpoicheck",
        "hwgeek": "com.sharedream.geek.plugin",
        "geekjk": "com.kj.wangushengshi",
        "360watch": "com.sharedream.geek.demo.360watch",
        "ssui": "com.ssui.yourpage",
        "sogou": "com.sogou.iot",
        "mzquickapp": "com.meizu.assistant.quickapp",
        "journeyui": "com.journeyui.launcher",
        "forddemo": "com.ford.geek.demo",
        "ford": "com.ford.sync.scenariomode",
        "crgt": "com.crgt.ilife",
        "opponew": "com.coloros.assistantscreen",
        "unicdata": "",
        "crland": "com.crland.mixc",
        "jgtest": "com.jiguang.jiketest",
        "bytedance": "com.bytedance.bdlocation"
    }
    return PACKAGE_MAPPING.get(app_id)

@udf
def get_category(c_id_list,c_id_categories_map):
    # c_id查询分类
    c_name_list = []
    if not c_id_list:
        return '_'.join(['','',''])

    c_id_list = eval(c_id_list)

    if len(c_id_list) == 1:
        c_id_list.extend(['M','N'])

    if len(c_id_list) == 2:
        c_id_list.extend(['M'])

    for c_id in c_id_list:
        c_name_list.append(c_id_categories_map.get(c_id,''))

    return '_'.join(c_name_list)