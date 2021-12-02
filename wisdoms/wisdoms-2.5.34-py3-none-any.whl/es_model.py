# Created by Q-ays.
# whosqays@gmail.com


from elasticsearch_dsl import Document, InnerDoc, Text, Keyword, Integer, Float, Boolean, Ip, Object, Nested, Date, \
    GeoPoint

from wisdoms.ms import rpc_wrapper
from wisdoms.es_db import inner_o2d_filter
from wisdoms.dapr import dapr_invoke
from datetime import datetime


class EnumType(InnerDoc):
    name = Text(fields={'keyword': Keyword()})  # 枚举名称
    code = Text(fields={'keyword': Keyword()})  # 枚举code
    order = Integer()  # 序号


class Phone(Text):
    pass


class Email(Text):
    pass


class EnumObj(Object):
    pass


def enumObj():
    return EnumObj(EnumType)


def text_keyword():
    return Text(fields={'keyword': Keyword()})


def doc_spawn(MS_HOST, **kwargs):
    class BaseDocument(Document):
        user_ = Nested()
        org_ = Nested()
        addTime_ = Date()
        updTime_ = Date()
        status_ = Text()

        @classmethod
        def field2index_set(cls):
            try:
                cls.init()
            except Exception as e:
                print('es 模型初始化失败，模型字段类型可能冲突')
                print(e)

            try:

                index = cls.Index.name

                # todo 存表结构 return 表id
                res = dapr_invoke('base_app', '/indexSet/index_add',
                                  {'data': {'index': index,
                                            'status': kwargs.get('status', 'init'),
                                            'types': kwargs.get('types')
                                            }
                                   })

                if res.status_code == 200:
                    index_id = res.json().get('data').get('id')
                else:
                    print(res)
                    raise Exception('添加index表出错')

                datas = list()

                fields = cls._doc_type.mapping.properties._params.get(
                    'properties')

                i = 5
                for k in fields:
                    if k in ['user_', 'org_', 'status_', 'addTime_', 'updTime_']:
                        continue
                    data = dict()
                    data['index'] = index
                    data['index_id'] = index_id
                    data['field'] = k
                    data['sort'] = i
                    if isinstance(fields[k], EnumObj):
                        data['types'] = 'enum'
                        data['properties'] = [
                            'code', 'value', 'name', 'label', 'order']
                    elif isinstance(fields[k], Phone):
                        data['name'] = '电话'
                        data['types'] = 'phone'
                    elif isinstance(fields[k], Email):
                        data['name'] = '邮箱'
                        data['types'] = 'email'
                    elif isinstance(fields[k], Date):
                        data['name'] = '日期'
                        data['types'] = 'date'
                    elif isinstance(fields[k], Integer):
                        data['types'] = 'int'
                    elif isinstance(fields[k], Ip):
                        data['types'] = 'ip'
                    elif isinstance(fields[k], Nested):
                        data['types'] = 'nested'
                    # 这行代码需要放到最后的 else if
                    elif isinstance(fields[k], Text):
                        data['types'] = 'str'
                    else:
                        pass

                    datas.append(data)
                    i = i + 2

                print(datas)

                res = dapr_invoke(
                    'base_app', '/indexSet/field_adds', {'data': datas})
                print(res)

            except Exception as e:
                print('字段和表存入pg 失败')
                print(e)

        def dump(self, p=None):
            res = self.to_dict()

            inner_o2d_filter(res)

            d = dict()

            d['id'] = self.meta.id
            d['index'] = self.meta.index

            if p:
                for k in res:
                    if isinstance(res[k], dict):
                        d[k] = res[k].get(p, res[k])
                    else:
                        d[k] = res[k]

                return d
            else:
                return dict(d, **res)

        def save(self, *args, **kwargs):
            if not self.addTime_:
                self.addTime_ = datetime.now()

            return super().save(*args, **kwargs)

    return BaseDocument
