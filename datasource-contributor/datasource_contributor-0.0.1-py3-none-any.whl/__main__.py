import os

from scrapy.crawler import CrawlerProcess
from ROM.spiders.rom import RomSpider
import requests

TEST_SSO_DOMAIN = "http://192.168.12.156:32003"
TEST_DOMAIN = "http://192.168.12.156:32002"
PRODUCTION_SSO_DOMAIN = "http://sso.citybrain.org"
PRODUCTION_DOMAIN = "http://www.citybrain.org"
CURRENT_SSO_DOMAIN = ""
CURRENT_DOMAIN = ""

RDS = 1
ODPS = 3
USER_ID = -1

TOKEN = ""
EXEC = True
MENU_NUM = -1
URL = ""
USER_NAME = ""
PASS_WORD = ""
SPIDER_NAME = ""
OSS_ID = -1
BUCKET_NAME = ""
OSS_PATH = "52/54"


def login(username, password):
    """
    登录citybrain.org站点
    :param username:
    :param password:
    :return:
    """
    data = {
        "client_id": "csop",
        "username": username,
        "password": password,
        "grant_type": "password"
    }
    resp = requests.post("%s%s" % (CURRENT_SSO_DOMAIN, "/token"), json=data)
    data = resp.json()
    print("login data: %s" % data)
    # TODO: 登录是否成功
    return data['data']['access_token']


def osslist(token):
    """
    获取用户的oss列表
    :param token: 
    :return: 
    """
    headers = {
        "Authorization": "Bearer " + token
    }
    url = "%s%s" % (CURRENT_DOMAIN, "/api/cloudP/oss/list")
    print("url: %s" % url)
    resp = requests.get(url, headers=headers)
    data = resp.json()
    return data['data']


def bucket(id, path, token):
    """

    :param id:
    :param path:
    :param token:
    :return:
    """
    headers = {
        "Authorization": "Bearer " + token
    }
    data = {
        "id": id,
        "path": path
    }
    url = "%s%s" % (CURRENT_DOMAIN, "/api/dataNode/oss/bucket")
    print("url: %s" % url)
    resp = requests.post(url, json=data, headers=headers)
    data = resp.json()
    return data['data']


def library(instance_id, token):
    """
    获取library
    :param instance_id:
    :param token:
    :return:
    """
    headers = {
        "Authorization": "Bearer " + token
    }
    url = "%s%s%s%s" % (CURRENT_DOMAIN, "/api/cloudP/library/list?instance_id=", instance_id, "&page=1&page_size=100")
    print("url: %s" % url)
    resp = requests.get(url, headers=headers)
    data = resp.json()
    return data['data']


def check_table_name(library_id, table_name, token):
    """
    检查library中是否存在表名
    :param library_id:
    :param table_name:
    :param token:
    :return:
    """
    headers = {
        "Authorization": "Bearer " + token
    }
    url = "%s%s%s%s%s" % (
        CURRENT_DOMAIN, "/api/dataNode/check/tableName?library_id=", library_id, "&t_name=", table_name)
    print("url: %s" % url)
    resp = requests.get(url, headers=headers)
    data = resp.json()
    return data['data']


class BuildParam:
    description = ""
    # 贡献记录id
    id = -1
    instance_id = -1
    instance_name = ""
    instance_type = 1
    library_id = -1
    library_name = ""
    link_url = ""
    name = ""
    t_field = []
    t_name = ""


def build(build_param):
    """
    贡献数据
    :param build_param:
    :return:
    """
    data = {
        "description": build_param.description,
        "id": build_param.id,
        "instance_id": build_param.instance_id,
        "instance_name": build_param.instance_name,
        "instance_type": build_param.instance_type,
        "library_id": build_param.library_id,
        "library_name": build_param.library_name,
        "link_url": build_param.link_url,
        "name": build_param.name,
        "t_field": build_param.t_field,
        "t_name": build_param.t_name
    }
    headers = {
        "Authorization": "Bearer " + TOKEN
    }
    url = "%s%s" % (CURRENT_DOMAIN, "/api/dataNode/build")
    print("url: %s" % url)
    resp = requests.post(url, json=data, headers=headers)
    data = resp.json()
    return data['data']


def resource(product, token):
    """
    获取申请的RDS或者ODPS
    :param product:
    :param token:
    :return:
    """
    headers = {
        "Authorization": "Bearer " + token
    }
    url = "%s%s%s%s" % (CURRENT_DOMAIN, "/api/dataNode/apply/resource/list?produce_type=", product,
                        "&create_date_start=&create_date_end=&release_date_start=&release_date_end=&page=1&page_size=10"
                        )
    print("url: %s" % url)
    resp = requests.get(url, headers=headers)
    data = resp.json()
    return data['data']


def menu():
    """
    :return:
    """
    print("************************************")
    print("************爬虫系统CUI**************")
    print("************************************")
    print("**************菜单******************")
    print("--------------   -------------------")
    print("************************************")
    print("************************************")
    print("--------------1.login---------------")
    print("************************************")
    print("--------------2.crawl---------------")
    print("************************************")
    print("--------------3.exit----------------")
    print("************************************")
    print("--------------   -------------------")


def handle_login():
    """
    :return:
    """
    os.system("clear")
    username = input("请输入您的用户名：")
    global USER_NAME
    USER_NAME = username
    print("username: %s" % username)
    password = input("请输入您的密码： ")
    global PASS_WORD
    PASS_WORD = password
    print("password: %s" % password)
    global TOKEN
    TOKEN = login(username, password)
    print("token: %s" % TOKEN)


def handle_craw():
    """
    :return:
    """
    os.system("clear")
    spiderName = input("请输入爬虫名称： ")
    global SPIDER_NAME
    SPIDER_NAME = spiderName
    print("爬虫名称： %s" % spiderName)
    domain = input("请输入爬取的domin: ")
    print("domin: %s" % domain)
    url = input("请输入要爬取的网站的起始地址： ")
    print("url: %s" % url)
    global URL
    URL = url
    # process = CrawlerProcess()
    # # 'followall' is the name of one of the spiders of the project.
    # process.crawl(RomSpider)
    # process.start()  # the script will block here until the crawling is finished
    contribute_data()


def contribute_data():
    # step2: get user's resources
    rds = resource(RDS, TOKEN)
    print("rds: %s" % rds)
    rds_instance_id = rds[0]['instance_id']
    print("rds_instance_id: %s" % rds_instance_id)
    rds_instance_name = rds[0]['instance_name']
    print("rds_instance_name: %s" % rds_instance_name)
    odps = resource(ODPS, TOKEN)
    print("odps: %s" % odps)
    odps_instance_id = odps[0]['instance_id']
    print("odps_instance_id: %s" % odps_instance_id)
    # step3: get user's oss list
    oss = osslist(TOKEN)
    print("osslist: %s" % oss)
    oss_id = oss[0]['oss_id']
    print("oss_id: %s" % oss_id)
    global OSS_ID
    OSS_ID = oss_id
    bucket_name = oss[0]['bucket_name']
    print("bucket_name: %s" % bucket_name)
    global BUCKET_NAME
    BUCKET_NAME = bucket_name
    # osslist: [{'oss_id': 24, 'bucket_name': 'gcyzs-bucket'}]
    # step4: get oss bucket to return rows
    rows = bucket(OSS_ID, OSS_PATH, TOKEN)
    print("rows: %s" % rows)
    # step5: get odps's library list
    library_list = library(rds_instance_id, TOKEN)
    print("library list: %s" % library_list)
    library_id = library_list[0]['id']
    print("library_id: %s" % library_id)
    library_name = library_list[0]['library_name']
    print("library_name: %s" % library_name)
    # step6: check table name exist in library or not
    table_name = input("请输入数据要保存的表名： ")
    exist = check_table_name(library_id, table_name, TOKEN)
    print("exist: %s" % exist)
    # step7: contribute data
    build_param = BuildParam()
    build_param.description = URL
    build_param.id = rows['id']
    build_param.instance_id = rds_instance_id
    build_param.instance_name = rds_instance_name
    build_param.instance_type = RDS
    build_param.library_id = library_id
    build_param.library_name = library_name
    build_param.link_url = URL
    build_param.name = USER_NAME + "_" + str(rds_instance_id) + "_" + str(library_id) + "_" + SPIDER_NAME
    build_param.t_field = rows['rows']

    build_param.t_name = table_name
    print("build_param: %s" % build_param)
    build_resp = build(build_param)
    print("build_resp: %s" % build_resp)


if __name__ == "__main__":
    CURRENT_SSO_DOMAIN = TEST_SSO_DOMAIN
    CURRENT_DOMAIN = TEST_DOMAIN
    while True:
        menu()
        MENU_NUM = input("please input menu number: ")
        if MENU_NUM == '1':
            handle_login()
        elif MENU_NUM == '2':
            handle_craw()
        else:
            break

# if __name__ == "__main__":
#     CURRENT_SSO_DOMAIN = TEST_SSO_DOMAIN
#     CURRENT_DOMAIN = TEST_DOMAIN
#     os.system('cd /Users/tianrang/PycharmProjects/datasource-contributor/rowm/rowm && scrapy crawl rom')
#     print(os.path.abspath(''))
#     print(os.path.abspath('') + '/row.csv')
#     # step1: input username and password to login
#     username = input("请输入您的用户名：")
#     print("username: %s" % username)
#     password = input("请输入您的密码： ")
#     print("password: %s" % password)
#     # step 1.3 scrapy
#     spiderName = input("请输入爬虫名称： ")
#     domain = input("请输入爬取的domin: ")
#     url = input("请输入要爬取的网站的起始地址： ")
#     print("url: %s" % url)
#
#     process = CrawlerProcess()
#
#     # 'followall' is the name of one of the spiders of the project.
#     process.crawl(RomSpider)
#     process.start()  # the script will block here until the crawling is finished
#     token = login(username, password)
#     print("token: %s" % token)
#     # step2: get user's resources
#     rds = resource(RDS, token)
#     print("rds: %s" % rds)
#     odps = resource(ODPS, token)
#     print("odps: %s" % odps)
#     # step3: get user's oss list
#     oss = osslist(token)
#     print("osslist: %s" % oss)
#     # osslist: [{'oss_id': 24, 'bucket_name': 'gcyzs-bucket'}]
#     # step4: get oss bucket to return rows
#     rows = bucket(24, '52/54', token)
#     print("rows: %s" % rows)
#     # step5: get odps's library list
#     libraryList = library(23, token)
#     print("library list: %s" % libraryList)
#     # step6: check table name exist in library or not
#     table_name = input("请输入数据要保存的表名： ")
#     exist = check_table_name(7, table_name, token)
#     print("exist: %s" % exist)
#     # step7: contribute data
#     build_param = BuildParam()
#     build_param.description = url
#     build_param.id = rows['id']
#     build_param.instance_id = 45
#     build_param.instance_name = "ODPS公共实例"
#     build_param.instance_type = 3
#     build_param.library_id = 20
#     build_param.library_name = "nsodps_dev"
#     build_param.link_url = url
#     build_param.name = "sdk"
#     build_param.t_field = rows['rows']
#
#     build_param.t_name = table_name
#     print("build_param: %s" % build_param)
#     build_resp = build(build_param)
#     print("build_resp: %s" % build_resp)
