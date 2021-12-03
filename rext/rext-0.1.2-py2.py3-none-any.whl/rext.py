__version__ = '0.1.2'

import pymongo
import pandas as pd
import os
import csv
import json


class mstring():

    # 空白符种类

    # ' '空格
    # '\t'水平制表符
    # '\n'换行
    # '\r'回车
    # '\f'换页
    # '\v'垂直制表符

    # 除去两端空格

    def remove_space_twoends(s):
        return s.strip()

    # 删除所有空格

    def remove_space_all(s):
        return s.replace(" ", "")

    # 利用翻译删除指定空白字符

    def remove_white_type(s, sign=' \t\n\r\f\v'):
        return s.translate(None, sign)

    # 删除所有空白符

    def remove_white_all(s):
        return ''.join(s.split())

    # 空白字符替换成空格

    def white2space(s, sign=' \t\n\r\f\v'):
        return s.translate(' ', sign)

    # 多个空格保留一个

    def muti2single_space(s):
        return ' '.join(s.split())

    # 对于来自钉钉云文档的csv下载 务必过滤\xa0
    def nbsp2space(s):
        return s.replace('\xa0', ' ')


class mlist():

    def from_csv(path, options):
        with open(path, 'r', encoding='utf-8-sig')as f:
            reader = csv.DictReader(f)
            data_list = []
            for each in reader:
                temp = each
                if temp[options["important_key"]]:
                    for key in temp.keys():
                        temp[key] = mstring.muti2single_space(mstring.remove_space_twoends(mstring.nbsp2space(temp[key])))
                    data_list.append(temp)
            return data_list

    def to_csv(data_list, columns, path):
        mos.check_dir_and_create(path)
        result_list = pd.DataFrame(columns=columns, data=data_list)
        result_list.to_csv(path, encoding='utf-8-sig', index=False)

    def from_json(path):
        with open(path, 'r', encoding='utf-8-sig') as f:
            pre_data_list = json.load(f)
            data_list = []
            for item in pre_data_list:
                data_list.append(item)
            return data_list

    def to_json(data_list, columns, path):
        mos.check_dir_and_create(path)
        result_list = pd.DataFrame(columns=columns, data=data_list)
        out = result_list.to_json(indent=4, orient='records', force_ascii=False)
        with open(path, 'w', encoding='utf-8-sig')as jsonfile:
            jsonfile.write(out)

    def from_mongodb(db, col, filter):

        mycol = db[col]
        dataCursor = mycol.find(filter)
        return list(dataCursor)


class mdict():
    pass


class mdb():

    def connect_mongodb(options):
        DB_HOST = options['DB_HOST']
        DB_PORT = options['DB_PORT']
        DB_USER = options['DB_USER']
        DB_PASS = options['DB_PASS']
        DB_DB = options['DB_DB']

        if DB_USER == "":
            myclient = pymongo.MongoClient("mongodb://%s:%s/" % (DB_HOST, DB_PORT))
        else:
            if DB_DB == "admin":
                myclient = pymongo.MongoClient("mongodb://%s:%s@%s:%s/" % (DB_USER, DB_PASS, DB_HOST, DB_PORT))
            else:
                myclient = pymongo.MongoClient("mongodb://%s:%s@%s:%s/%s" % (DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_DB))

        return myclient[DB_DB]


class mos():

    def check_dir_and_create(path):
        data_dir = "/".join(path.split("/")[0:-1])
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)


def main():
    pass


if __name__ == '__main__':
    main()
