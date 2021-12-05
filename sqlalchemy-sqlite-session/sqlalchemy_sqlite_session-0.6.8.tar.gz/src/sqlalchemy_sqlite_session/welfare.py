from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session
import time
import json


Base = declarative_base()
# generate tables
# engine = create_engine("mysql+pymysql://root:Wangchenyu2012@localhost:3306/sd")
# Base.metadata.create_all(engine)


def database_toast(issue: int, name_cn: str, name: str, key: str, value: str):
    """数据表属性 写入成功提示"""
    print(f">>> 合并数据成功，期号：{issue}，表名：{name_cn}-{name}: {key} - {value}")


def get_session_welfare():
    # path_db = r'C:\Users\Wangjulong\tensorflows\sd.db'
    # path_str = 'sqlite:///' + path_db
    # db_engine = create_engine(path_str, echo=False)
    # session = Session(db_engine)
    # return session
    # mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]
    engine = create_engine("mysql+pymysql://root:Wangchenyu2012@127.0.0.1:3306/sd")
    session = Session(engine)
    return session


class WelfareNumber(Base):
    """ numbers@sd.db """
    __tablename__ = 'numbers'

    issue = Column(Integer, primary_key=True)
    num1 = Column(Integer, nullable=False)
    num2 = Column(Integer, nullable=False)
    num3 = Column(Integer, nullable=False)

    def __init__(self, data_list: list):
        self.issue, self.num1, self.num2, self.num3 = data_list

    @classmethod
    def get_issues(cls):
        """get issues[list]"""
        session = get_session_welfare()
        i = session.query(cls).all()
        session.close()
        result = [x.issue for x in i]
        result.sort()
        return result

    @classmethod
    def get_previous3_issues(cls, issue_now):
        all_issues = cls.get_issues()
        all_issues.sort()
        issue_now = int(issue_now)
        index_now = all_issues.index(issue_now)
        return all_issues[index_now - 3: index_now]

    @classmethod
    def get_next3_issues(cls, issue_now):
        all_issues = cls.get_issues()
        issue_now = int(issue_now)
        index_now = all_issues.index(issue_now)
        return all_issues[index_now + 1: index_now + 4]

    @classmethod
    def get_all(cls):
        """get all [[issue, num1, num2, num3]... ]"""
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        return [[x.issue, x.num1, x.num2, x.num3] for x in data]

    @classmethod
    def get_numbers(cls):
        """get numbers [[issue, num1, num2, num3]... ]"""
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[x.issue, x.num1, x.num2, x.num3] for x in data]
        return result

    @classmethod
    def get_one(cls, issue_number: int):
        """获取对应 issue 的号码列表 [issue, num1, num2, num3]"""
        session = get_session_welfare()
        data = session.query(cls).get(issue_number)
        session.close()
        return [data.issue, data.num1, data.num2, data.num3]

    @classmethod
    def get_num1(cls, issue_number: int):
        """获取对应 issue 的号码 num1"""
        session = get_session_welfare()
        data = session.query(cls).get(issue_number)
        session.close()
        return data.num1

    @classmethod
    def get_num2(cls, issue_number: int):
        """获取对应 issue 的号码 num2"""
        session = get_session_welfare()
        data = session.query(cls).get(issue_number)
        session.close()
        return data.num2

    @classmethod
    def get_num3(cls, issue_number: int):
        """获取对应 issue 的号码 num3"""
        session = get_session_welfare()
        data = session.query(cls).get(issue_number)
        session.close()
        return data.num3

    @classmethod
    def add_number(cls, p_issue: str, p_numbers: list):
        """添加一条记录"""
        session = get_session_welfare()
        ins = WelfareNumber([p_issue] + p_numbers)
        session.merge(ins)
        session.commit()
        session.close()
        print(f">>> merge kill in kills:{p_issue} - {p_numbers}")


class WelfareCollectionEvaluate(Base):
    __tablename__ = 'collection_evaluates'

    name = Column(String(50), primary_key=True)
    rate = Column(Integer, nullable=False)

    @classmethod
    def get_all(cls):
        """
        根据名称获取对应的设置项的值
        :param name: 设置项名称
        :return: 根据值的属性，返回对应的数据类型
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[x.name, x.rate] for x in data]
        return result


class WelfareCollectionKill(Base):
    __tablename__ = 'collection_kills'
    name = Column(String(50), primary_key=True)
    issue = Column(Integer, primary_key=True)
    kill1 = Column(Integer, nullable=False)
    kill2 = Column(Integer)
    kill3 = Column(Integer)
    correct = Column(Integer)

    @classmethod
    def get_kills(cls):
        """
        根据名称获取对应的设置项的值
        :param name: 设置项名称
        :return: 根据值的属性，返回对应的数据类型
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[x.name, x.issue, x.kill1, x.kill2, x.kill3, x.correct] for x in data]
        return result

    @classmethod
    def add_kill(cls, p_name: str, p_issue: str, p_kills: list):
        session = get_session_welfare()
        ins = cls()
        ins.name = p_name
        ins.issue = p_issue
        ins.kill1 = p_kills[0]
        if len(p_kills) > 1:
            ins.kill2 = p_kills[1]
        if len(p_kills) > 2:
            ins.kill3 = p_kills[2]
        session.merge(ins)
        session.commit()
        session.close()
        print(f">>> merge kill in kills:{p_name} - {p_issue} - {p_kills}")


class WelfareCollectionName(Base):
    __tablename__ = 'collection_names'

    name = Column(String(50), primary_key=True)

    @classmethod
    def get_names(cls):
        """
        根据名称获取对应的设置项的值
        :param name: 设置项名称
        :return: 根据值的属性，返回对应的数据类型
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [x.name for x in data]
        return result

    @classmethod
    def add_name(cls, name_add: str):
        session = get_session_welfare()
        ins = cls()
        ins.name = name_add
        session.merge(ins)
        session.commit()
        session.close()
        print(f">>> merge name in Table Name, name is {name_add}")

    @classmethod
    def remove_name(cls, name_remove: str):
        session = get_session_welfare()
        ins = session.query(cls).filter_by(name=name_remove).first()
        session.delete(ins)
        session.commit()
        session.close()


class WelfareConfig(Base):
    __tablename__ = 'configs'

    name = Column(String(50), primary_key=True)
    value = Column(String(50))

    def __init__(self, name, value):
        self.name = name
        self.value = value

    @classmethod
    def get_all(cls):
        """
        获取所有的数据
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = {x.name: x.value for x in data}
        return result

    @classmethod
    def get_item(cls, the_key: str):
        """get value"""
        session = get_session_welfare()
        data = session.query(cls).get(the_key)
        session.close()
        return data.value

    @classmethod
    def set_item(cls, the_key: str, the_value: str):
        """set value"""
        session = get_session_welfare()
        data = session.query(cls).get(the_key)
        data.value = the_value
        session.merge(data)
        session.commit()
        session.close()

    @classmethod
    def add_item(cls, the_key: str, the_value: str):
        """add item"""
        session = get_session_welfare()
        ins = cls(the_key, the_value)
        session.merge(ins)
        session.commit()
        session.close()
        print(f">>> add item success, name: {the_key}, value: {the_value}")


class WelfareFollow1(Base):
    __tablename__ = 'follow1'
    issue = Column(Integer, primary_key=True)
    num1 = Column(Integer, nullable=False)
    num2 = Column(Integer, nullable=False)
    num3 = Column(Integer, nullable=False)
    next1 = Column(Integer)
    next2 = Column(Integer)
    next3 = Column(Integer)
    f00 = Column(Integer)
    f01 = Column(Integer)
    f02 = Column(Integer)
    f03 = Column(Integer)
    f04 = Column(Integer)
    f05 = Column(Integer)
    f06 = Column(Integer)
    f07 = Column(Integer)
    f08 = Column(Integer)
    f09 = Column(Integer)
    f10 = Column(Integer)
    f11 = Column(Integer)
    f12 = Column(Integer)
    f13 = Column(Integer)
    f14 = Column(Integer)
    f15 = Column(Integer)
    f16 = Column(Integer)
    f17 = Column(Integer)
    f18 = Column(Integer)
    f19 = Column(Integer)
    f20 = Column(Integer)
    f21 = Column(Integer)
    f22 = Column(Integer)
    f23 = Column(Integer)
    f24 = Column(Integer)
    f25 = Column(Integer)
    f26 = Column(Integer)
    f27 = Column(Integer)
    f28 = Column(Integer)
    f29 = Column(Integer)
    f30 = Column(Integer)
    f31 = Column(Integer)
    f32 = Column(Integer)
    f33 = Column(Integer)
    f34 = Column(Integer)
    f35 = Column(Integer)
    f36 = Column(Integer)
    f37 = Column(Integer)
    f38 = Column(Integer)
    f39 = Column(Integer)
    f40 = Column(Integer)
    f41 = Column(Integer)
    f42 = Column(Integer)
    f43 = Column(Integer)
    f44 = Column(Integer)
    f45 = Column(Integer)
    f46 = Column(Integer)
    f47 = Column(Integer)
    f48 = Column(Integer)
    f49 = Column(Integer)
    f50 = Column(Integer)
    f51 = Column(Integer)
    f52 = Column(Integer)
    f53 = Column(Integer)
    f54 = Column(Integer)
    f55 = Column(Integer)
    f56 = Column(Integer)
    f57 = Column(Integer)
    f58 = Column(Integer)
    f59 = Column(Integer)
    f60 = Column(Integer)
    f61 = Column(Integer)
    f62 = Column(Integer)
    f63 = Column(Integer)
    f64 = Column(Integer)
    f65 = Column(Integer)
    f66 = Column(Integer)
    f67 = Column(Integer)
    f68 = Column(Integer)
    f69 = Column(Integer)
    f70 = Column(Integer)
    f71 = Column(Integer)
    f72 = Column(Integer)
    f73 = Column(Integer)
    f74 = Column(Integer)
    f75 = Column(Integer)
    f76 = Column(Integer)
    f77 = Column(Integer)
    f78 = Column(Integer)
    f79 = Column(Integer)
    f80 = Column(Integer)
    f81 = Column(Integer)
    f82 = Column(Integer)
    f83 = Column(Integer)
    f84 = Column(Integer)
    f85 = Column(Integer)
    f86 = Column(Integer)
    f87 = Column(Integer)
    f88 = Column(Integer)
    f89 = Column(Integer)
    f90 = Column(Integer)
    f91 = Column(Integer)
    f92 = Column(Integer)
    f93 = Column(Integer)
    f94 = Column(Integer)
    f95 = Column(Integer)
    f96 = Column(Integer)
    f97 = Column(Integer)
    f98 = Column(Integer)
    f99 = Column(Integer)

    def __init__(self, issue, n1, n2, n3) -> None:
        super().__init__()
        self.issue = issue
        self.num1 = n1
        self.num2 = n2
        self.num3 = n3

    @classmethod
    def get_follow_4049(cls):
        session = get_session_welfare()
        data = session.query(cls).all()
        result = {}
        for t in data:
            result[t.issue] = [t.f40, t.f41, t.f42, t.f43, t.f44, t.f45, t.f46, t.f47, t.f48, t.f49]
        return result

    @classmethod
    def get_numbers(cls):
        """
        [[issue, num1, num2, num3],...]
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[x.issue, x.num1, x.num2, x.num3] for x in data]
        return result

    @classmethod
    def get_number_and_next(cls):
        """
        [[issue, num1, num2, num3, next1, next2, next3],...]
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[x.issue, x.num1, x.num2, x.num3, x.next1, x.next2, x.next3] for x in data]
        return result

    @classmethod
    def get_all(cls):
        """
        获取所有的数据
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[
            x.issue,
            x.num1,
            x.num2,
            x.num3,
            x.next1,
            x.next2,
            x.next3,
            x.f00,
            x.f01,
            x.f02,
            x.f03,
            x.f04,
            x.f05,
            x.f06,
            x.f07,
            x.f08,
            x.f09,
            x.f10,
            x.f11,
            x.f12,
            x.f13,
            x.f14,
            x.f15,
            x.f16,
            x.f17,
            x.f18,
            x.f19,
            x.f20,
            x.f21,
            x.f22,
            x.f23,
            x.f24,
            x.f25,
            x.f26,
            x.f27,
            x.f28,
            x.f29,
            x.f30,
            x.f31,
            x.f32,
            x.f33,
            x.f34,
            x.f35,
            x.f36,
            x.f37,
            x.f38,
            x.f39,
            x.f40,
            x.f41,
            x.f42,
            x.f43,
            x.f44,
            x.f45,
            x.f46,
            x.f47,
            x.f48,
            x.f49,
            x.f50,
            x.f51,
            x.f52,
            x.f53,
            x.f54,
            x.f55,
            x.f56,
            x.f57,
            x.f58,
            x.f59,
            x.f60,
            x.f61,
            x.f62,
            x.f63,
            x.f64,
            x.f65,
            x.f66,
            x.f67,
            x.f68,
            x.f69,
            x.f70,
            x.f71,
            x.f72,
            x.f73,
            x.f74,
            x.f75,
            x.f76,
            x.f77,
            x.f78,
            x.f79,
            x.f80,
            x.f81,
            x.f82,
            x.f83,
            x.f84,
            x.f85,
            x.f86,
            x.f87,
            x.f88,
            x.f89,
            x.f90,
            x.f91,
            x.f92,
            x.f93,
            x.f94,
            x.f95,
            x.f96,
            x.f97,
            x.f98,
            x.f99
        ] for x in data]
        return result

    @classmethod
    def get_issues(cls):
        """get issues"""
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [x.issue for x in data]
        result.sort()
        return result


class WelfareFollow2(Base):
    __tablename__ = 'follow2'
    issue = Column(Integer, primary_key=True)
    num1 = Column(Integer, nullable=False)
    num2 = Column(Integer, nullable=False)
    num3 = Column(Integer, nullable=False)
    next1 = Column(Integer)
    next2 = Column(Integer)
    next3 = Column(Integer)
    f00 = Column(Integer)
    f01 = Column(Integer)
    f02 = Column(Integer)
    f03 = Column(Integer)
    f04 = Column(Integer)
    f05 = Column(Integer)
    f06 = Column(Integer)
    f07 = Column(Integer)
    f08 = Column(Integer)
    f09 = Column(Integer)
    f10 = Column(Integer)
    f11 = Column(Integer)
    f12 = Column(Integer)
    f13 = Column(Integer)
    f14 = Column(Integer)
    f15 = Column(Integer)
    f16 = Column(Integer)
    f17 = Column(Integer)
    f18 = Column(Integer)
    f19 = Column(Integer)
    f20 = Column(Integer)
    f21 = Column(Integer)
    f22 = Column(Integer)
    f23 = Column(Integer)
    f24 = Column(Integer)
    f25 = Column(Integer)
    f26 = Column(Integer)
    f27 = Column(Integer)
    f28 = Column(Integer)
    f29 = Column(Integer)
    f30 = Column(Integer)
    f31 = Column(Integer)
    f32 = Column(Integer)
    f33 = Column(Integer)
    f34 = Column(Integer)
    f35 = Column(Integer)
    f36 = Column(Integer)
    f37 = Column(Integer)
    f38 = Column(Integer)
    f39 = Column(Integer)
    f40 = Column(Integer)
    f41 = Column(Integer)
    f42 = Column(Integer)
    f43 = Column(Integer)
    f44 = Column(Integer)
    f45 = Column(Integer)
    f46 = Column(Integer)
    f47 = Column(Integer)
    f48 = Column(Integer)
    f49 = Column(Integer)
    f50 = Column(Integer)
    f51 = Column(Integer)
    f52 = Column(Integer)
    f53 = Column(Integer)
    f54 = Column(Integer)
    f55 = Column(Integer)
    f56 = Column(Integer)
    f57 = Column(Integer)
    f58 = Column(Integer)
    f59 = Column(Integer)
    f60 = Column(Integer)
    f61 = Column(Integer)
    f62 = Column(Integer)
    f63 = Column(Integer)
    f64 = Column(Integer)
    f65 = Column(Integer)
    f66 = Column(Integer)
    f67 = Column(Integer)
    f68 = Column(Integer)
    f69 = Column(Integer)
    f70 = Column(Integer)
    f71 = Column(Integer)
    f72 = Column(Integer)
    f73 = Column(Integer)
    f74 = Column(Integer)
    f75 = Column(Integer)
    f76 = Column(Integer)
    f77 = Column(Integer)
    f78 = Column(Integer)
    f79 = Column(Integer)
    f80 = Column(Integer)
    f81 = Column(Integer)
    f82 = Column(Integer)
    f83 = Column(Integer)
    f84 = Column(Integer)
    f85 = Column(Integer)
    f86 = Column(Integer)
    f87 = Column(Integer)
    f88 = Column(Integer)
    f89 = Column(Integer)
    f90 = Column(Integer)
    f91 = Column(Integer)
    f92 = Column(Integer)
    f93 = Column(Integer)
    f94 = Column(Integer)
    f95 = Column(Integer)
    f96 = Column(Integer)
    f97 = Column(Integer)
    f98 = Column(Integer)
    f99 = Column(Integer)

    def __init__(self, issue, n1, n2, n3) -> None:
        super().__init__()
        self.issue = issue
        self.num1 = n1
        self.num2 = n2
        self.num3 = n3

    @classmethod
    def get_follow_4049(cls):
        session = get_session_welfare()
        data = session.query(cls).all()
        result = {}
        for t in data:
            result[t.issue] = [t.f40, t.f41, t.f42, t.f43, t.f44, t.f45, t.f46, t.f47, t.f48, t.f49]
        return result

    @classmethod
    def get_numbers(cls):
        """
        [[issue, num1, num2, num3],...]
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[x.issue, x.num1, x.num2, x.num3] for x in data]
        return result

    @classmethod
    def get_number_and_next(cls):
        """
        [[issue, num1, num2, num3, next1, next2, next3],...]
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[x.issue, x.num1, x.num2, x.num3, x.next1, x.next2, x.next3] for x in data]
        return result

    @classmethod
    def get_all(cls):
        """
        获取所有的数据
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[
            x.issue,
            x.num1,
            x.num2,
            x.num3,
            x.next1,
            x.next2,
            x.next3,
            x.f00,
            x.f01,
            x.f02,
            x.f03,
            x.f04,
            x.f05,
            x.f06,
            x.f07,
            x.f08,
            x.f09,
            x.f10,
            x.f11,
            x.f12,
            x.f13,
            x.f14,
            x.f15,
            x.f16,
            x.f17,
            x.f18,
            x.f19,
            x.f20,
            x.f21,
            x.f22,
            x.f23,
            x.f24,
            x.f25,
            x.f26,
            x.f27,
            x.f28,
            x.f29,
            x.f30,
            x.f31,
            x.f32,
            x.f33,
            x.f34,
            x.f35,
            x.f36,
            x.f37,
            x.f38,
            x.f39,
            x.f40,
            x.f41,
            x.f42,
            x.f43,
            x.f44,
            x.f45,
            x.f46,
            x.f47,
            x.f48,
            x.f49,
            x.f50,
            x.f51,
            x.f52,
            x.f53,
            x.f54,
            x.f55,
            x.f56,
            x.f57,
            x.f58,
            x.f59,
            x.f60,
            x.f61,
            x.f62,
            x.f63,
            x.f64,
            x.f65,
            x.f66,
            x.f67,
            x.f68,
            x.f69,
            x.f70,
            x.f71,
            x.f72,
            x.f73,
            x.f74,
            x.f75,
            x.f76,
            x.f77,
            x.f78,
            x.f79,
            x.f80,
            x.f81,
            x.f82,
            x.f83,
            x.f84,
            x.f85,
            x.f86,
            x.f87,
            x.f88,
            x.f89,
            x.f90,
            x.f91,
            x.f92,
            x.f93,
            x.f94,
            x.f95,
            x.f96,
            x.f97,
            x.f98,
            x.f99
        ] for x in data]
        return result

    @classmethod
    def get_issues(cls):
        """get issues"""
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [x.issue for x in data]
        result.sort()
        return result


class WelfareFollow3(Base):
    __tablename__ = 'follow3'
    issue = Column(Integer, primary_key=True)
    num1 = Column(Integer, nullable=False)
    num2 = Column(Integer, nullable=False)
    num3 = Column(Integer, nullable=False)
    next1 = Column(Integer)
    next2 = Column(Integer)
    next3 = Column(Integer)
    f00 = Column(Integer)
    f01 = Column(Integer)
    f02 = Column(Integer)
    f03 = Column(Integer)
    f04 = Column(Integer)
    f05 = Column(Integer)
    f06 = Column(Integer)
    f07 = Column(Integer)
    f08 = Column(Integer)
    f09 = Column(Integer)
    f10 = Column(Integer)
    f11 = Column(Integer)
    f12 = Column(Integer)
    f13 = Column(Integer)
    f14 = Column(Integer)
    f15 = Column(Integer)
    f16 = Column(Integer)
    f17 = Column(Integer)
    f18 = Column(Integer)
    f19 = Column(Integer)
    f20 = Column(Integer)
    f21 = Column(Integer)
    f22 = Column(Integer)
    f23 = Column(Integer)
    f24 = Column(Integer)
    f25 = Column(Integer)
    f26 = Column(Integer)
    f27 = Column(Integer)
    f28 = Column(Integer)
    f29 = Column(Integer)
    f30 = Column(Integer)
    f31 = Column(Integer)
    f32 = Column(Integer)
    f33 = Column(Integer)
    f34 = Column(Integer)
    f35 = Column(Integer)
    f36 = Column(Integer)
    f37 = Column(Integer)
    f38 = Column(Integer)
    f39 = Column(Integer)
    f40 = Column(Integer)
    f41 = Column(Integer)
    f42 = Column(Integer)
    f43 = Column(Integer)
    f44 = Column(Integer)
    f45 = Column(Integer)
    f46 = Column(Integer)
    f47 = Column(Integer)
    f48 = Column(Integer)
    f49 = Column(Integer)
    f50 = Column(Integer)
    f51 = Column(Integer)
    f52 = Column(Integer)
    f53 = Column(Integer)
    f54 = Column(Integer)
    f55 = Column(Integer)
    f56 = Column(Integer)
    f57 = Column(Integer)
    f58 = Column(Integer)
    f59 = Column(Integer)
    f60 = Column(Integer)
    f61 = Column(Integer)
    f62 = Column(Integer)
    f63 = Column(Integer)
    f64 = Column(Integer)
    f65 = Column(Integer)
    f66 = Column(Integer)
    f67 = Column(Integer)
    f68 = Column(Integer)
    f69 = Column(Integer)
    f70 = Column(Integer)
    f71 = Column(Integer)
    f72 = Column(Integer)
    f73 = Column(Integer)
    f74 = Column(Integer)
    f75 = Column(Integer)
    f76 = Column(Integer)
    f77 = Column(Integer)
    f78 = Column(Integer)
    f79 = Column(Integer)
    f80 = Column(Integer)
    f81 = Column(Integer)
    f82 = Column(Integer)
    f83 = Column(Integer)
    f84 = Column(Integer)
    f85 = Column(Integer)
    f86 = Column(Integer)
    f87 = Column(Integer)
    f88 = Column(Integer)
    f89 = Column(Integer)
    f90 = Column(Integer)
    f91 = Column(Integer)
    f92 = Column(Integer)
    f93 = Column(Integer)
    f94 = Column(Integer)
    f95 = Column(Integer)
    f96 = Column(Integer)
    f97 = Column(Integer)
    f98 = Column(Integer)
    f99 = Column(Integer)

    def __init__(self, issue, n1, n2, n3) -> None:
        super().__init__()
        self.issue = issue
        self.num1 = n1
        self.num2 = n2
        self.num3 = n3

    @classmethod
    def get_follow_4049(cls):
        session = get_session_welfare()
        data = session.query(cls).all()
        result = {}
        for t in data:
            result[t.issue] = [t.f40, t.f41, t.f42, t.f43, t.f44, t.f45, t.f46, t.f47, t.f48, t.f49]
        return result

    @classmethod
    def get_numbers(cls):
        """
        [[issue, num1, num2, num3],...]
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[x.issue, x.num1, x.num2, x.num3] for x in data]
        return result

    @classmethod
    def get_number_and_next(cls):
        """
        [[issue, num1, num2, num3, next1, next2, next3],...]
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[x.issue, x.num1, x.num2, x.num3, x.next1, x.next2, x.next3] for x in data]
        return result

    @classmethod
    def get_all(cls):
        """
        获取所有的数据
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[
            x.issue,
            x.num1,
            x.num2,
            x.num3,
            x.next1,
            x.next2,
            x.next3,
            x.f00,
            x.f01,
            x.f02,
            x.f03,
            x.f04,
            x.f05,
            x.f06,
            x.f07,
            x.f08,
            x.f09,
            x.f10,
            x.f11,
            x.f12,
            x.f13,
            x.f14,
            x.f15,
            x.f16,
            x.f17,
            x.f18,
            x.f19,
            x.f20,
            x.f21,
            x.f22,
            x.f23,
            x.f24,
            x.f25,
            x.f26,
            x.f27,
            x.f28,
            x.f29,
            x.f30,
            x.f31,
            x.f32,
            x.f33,
            x.f34,
            x.f35,
            x.f36,
            x.f37,
            x.f38,
            x.f39,
            x.f40,
            x.f41,
            x.f42,
            x.f43,
            x.f44,
            x.f45,
            x.f46,
            x.f47,
            x.f48,
            x.f49,
            x.f50,
            x.f51,
            x.f52,
            x.f53,
            x.f54,
            x.f55,
            x.f56,
            x.f57,
            x.f58,
            x.f59,
            x.f60,
            x.f61,
            x.f62,
            x.f63,
            x.f64,
            x.f65,
            x.f66,
            x.f67,
            x.f68,
            x.f69,
            x.f70,
            x.f71,
            x.f72,
            x.f73,
            x.f74,
            x.f75,
            x.f76,
            x.f77,
            x.f78,
            x.f79,
            x.f80,
            x.f81,
            x.f82,
            x.f83,
            x.f84,
            x.f85,
            x.f86,
            x.f87,
            x.f88,
            x.f89,
            x.f90,
            x.f91,
            x.f92,
            x.f93,
            x.f94,
            x.f95,
            x.f96,
            x.f97,
            x.f98,
            x.f99
        ] for x in data]
        return result

    @classmethod
    def get_issues(cls):
        """get issues"""
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [x.issue for x in data]
        result.sort()
        return result


class WelfareResult(Base):
    __tablename__ = 'results'
    issue = Column(Integer, primary_key=True)
    num1 = Column(Integer, nullable=False)
    num2 = Column(Integer, nullable=False)
    num3 = Column(Integer, nullable=False)
    next1 = Column(Integer)
    next2 = Column(Integer)
    next3 = Column(Integer)
    size_position1 = Column(Integer)
    size_position2 = Column(Integer)
    size_position3 = Column(Integer)
    odd_position1 = Column(Integer)
    odd_position2 = Column(Integer)
    odd_position3 = Column(Integer)
    prime_position1 = Column(Integer)
    prime_position2 = Column(Integer)
    prime_position3 = Column(Integer)
    sum_size = Column(Integer)
    sum_odd = Column(Integer)
    sum_tail_size = Column(Integer)
    sum_tail_prime = Column(Integer)
    span = Column(Integer)

    def __init__(self, issue, n1, n2, n3):
        self.issue = issue
        self.num1 = n1
        self.num2 = n2
        self.num3 = n3

    @classmethod
    def get_column_names(cls):
        """
        get_column_names
        """
        return [
            "issue",
            "num1",
            "num2",
            "num3",
            "next1",
            "next2",
            "next3",
            "size_position1",
            "size_position2",
            "size_position3",
            "odd_position1",
            "odd_position2",
            "odd_position3",
            "prime_position1",
            "prime_position2",
            "prime_position3",
            "sum_size",
            "sum_odd",
            "sum_tail_size",
            "sum_tail_prime",
            "span"
        ]

    @classmethod
    def get_numbers(cls):
        """
        根据名称获取对应的设置项的值
        :param name: 设置项名称
        :return: 根据值的属性，返回对应的数据类型
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[x.issue, x.num1, x.num2, x.num3] for x in data]
        return result

    @classmethod
    def get_all(cls):
        """
        获取所有的数据
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[
            x.issue,
            x.num1,
            x.num2,
            x.num3,
            x.next1,
            x.next2,
            x.next3,
            x.size_position1,
            x.size_position2,
            x.size_position3,
            x.odd_position1,
            x.odd_position2,
            x.odd_position3,
            x.prime_position1,
            x.prime_position2,
            x.prime_position3,
            x.sum_size,
            x.sum_odd,
            x.sum_tail_size,
            x.sum_tail_prime,
            x.span
        ] for x in data]
        return result

    @classmethod
    def get_issues(cls):
        """get issues"""
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [x.issue for x in data]
        result.sort()
        return result


class BaXianGuoHai(Base):
    """
    kill1
    save1
    save2
    save3
    mix4
    mix5
    mix6
    mix7
    he
    span
    multi6
    multi3
    """
    __tablename__ = 'wx_baxianguohai'
    _name_ = '八仙过海'
    issue = Column(Integer, primary_key=True)

    # attributes
    kill1 = Column(String(50))  # 本期杀码
    save1 = Column(String(50))  # 毒胆参考
    save2 = Column(String(50))  # 双胆预测
    save3 = Column(String(50))  # 胆码推荐
    mix4 = Column(String(50))  # 精选四码
    mix5 = Column(String(50))  # 主打五码
    mix6 = Column(String(50))  # 缩水六码
    mix7 = Column(String(50))  # 盈利七码
    he = Column(String(50))  # 重点和值
    span = Column(String(50))  # 跨度参考
    multi6 = Column(String(500))  # 精选单注
    multi3 = Column(String(500))  # 防组选三

    # verify attributes
    v_kill1 = Column(String(50))
    v_save1 = Column(String(50))
    v_save2 = Column(String(50))
    v_save3 = Column(String(50))
    v_mix4 = Column(String(50))
    v_mix5 = Column(String(50))
    v_mix6 = Column(String(50))
    v_mix7 = Column(String(50))
    v_he = Column(String(50))
    v_span = Column(String(50))
    v_multi6 = Column(String(50))
    v_multi3 = Column(String(50))

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        本期杀码: kill1 \n
        毒胆参考: save1 \n
        双胆预测: save2 \n
        胆码推荐: save3 \n
        精选四码: mix4 \n
        主打五码: mix5 \n
        缩水六码: mix6 \n
        盈利七码: mix7 \n
        重点和值: he \n
        跨度参考: span \n
        精选单注: multi6 \n
        防组选三: multi3 \n
        @param issue: 期号 \n
        @param attribute_name: 属性名称 \n
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x) for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '') for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__, attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            '√' if self.v_kill1.find('正确') > -1 else '×',
            '√' if self.v_save1.find('正确') > -1 else '×',
            '√' if self.v_save2.find('正确') > -1 else '×',
            '√' if self.v_save3.find('正确') > -1 else '×',
            '√' if self.v_mix4.find('正确') > -1 else '×',
            '√' if self.v_mix5.find('正确') > -1 else '×',
            '√' if self.v_mix6.find('正确') > -1 else '×',
            '√' if self.v_mix7.find('正确') > -1 else '×',
            '√' if self.v_he.find('正确') > -1 else '×',
            '√' if self.v_span.find('正确') > -1 else '×',
            '√' if self.v_multi6.find('正确') > -1 else '×',
            '√' if self.v_multi3.find('正确') > -1 else '×'
        ]

    @classmethod
    def get_next_issue(cls):
        sess = get_session_welfare()
        all = sess.query(cls).all()
        i = all[-1].issue
        return i


class DaLaoRen(Base):
    __tablename__ = 'wx_dalaoren'
    _name_ = '大老人'
    issue = Column(Integer, primary_key=True)

    # attributes
    save3 = Column(String(50))  # 胆码
    save1 = Column(String(50))  # 金胆
    mix6 = Column(String(50))  # 复式组选
    kill1 = Column(String(50))  # 杀码
    shape = Column(String(50))  # 重点
    d2_combine = Column(String(50))  # 二码组合
    kill_d2_combine = Column(String(50))  # 杀二码组合
    multi6 = Column(String(500))  # 组选大底
    multi12 = Column(String(500))  # 精选12注

    # verify attributes
    v_save3 = Column(String(50))  # 胆码
    v_save1 = Column(String(50))  # 金胆
    v_mix6 = Column(String(50))  # 复式组选
    v_kill1 = Column(String(50))  # 杀码
    v_shape = Column(String(50))  # 重点
    v_d2_combine = Column(String(50))  # 二码组合
    v_kill_d2_combine = Column(String(50))  # 杀二码组合
    v_multi6 = Column(String(50))  # 组选大底
    v_multi12 = Column(String(50))  # 精选12注

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        胆码:      save3  \n
        金胆:      save1  \n
        复式组选:   mix6   \n
        杀码:      kill1  \n
        重点:      shape  \n
        二码组合:   d2_combine \n
        杀二码组合: kill_d2_combine    \n
        组选大底:  multi6 \n
        精选12注:  multi12    \n
        @param issue: 期号
        @param attribute_name: 属性名称
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x)
                       for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '')
                      for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__,
                       attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            '√' if self.v_save3.find('正确') > -1 else '×',
            '√' if self.v_save1.find('正确') > -1 else '×',
            '√' if self.v_mix6.find('正确') > -1 else '×',
            '√' if self.v_kill1.find('正确') > -1 else '×',
            '√' if self.v_shape.find('正确') > -1 else '×',
            '√' if self.v_d2_combine.find('正确') > -1 else '×',
            '√' if self.v_kill_d2_combine.find('正确') > -1 else '×',
            '√' if self.v_multi6.find('正确') > -1 else '×',
            '√' if self.v_multi12.find('正确') > -1 else '×'
        ]


class QingQiuJuShi(Base):
    __tablename__ = 'wx_qingqiujushi'
    _name_ = '清秋居士'
    issue = Column(Integer, primary_key=True)

    # attributes
    save1 = Column(String(50))  # 独胆
    save2 = Column(String(50))  # 双胆
    save3 = Column(String(50))  # 三胆
    kill1 = Column(String(50))  # 杀一码
    kill2 = Column(String(50))  # 杀二码
    kill3 = Column(String(50))  # 杀三码
    mix5 = Column(String(50))  # 五码
    mix6 = Column(String(50))  # 六码
    position_x = Column(String(50))  # 定位
    he = Column(String(50))  # 和值
    span = Column(String(50))  # 跨度
    multi6 = Column(String(500))  # 组选

    # verify attributes
    v_save1 = Column(String(50))
    v_save2 = Column(String(50))
    v_save3 = Column(String(50))
    v_kill1 = Column(String(50))
    v_kill2 = Column(String(50))
    v_kill3 = Column(String(50))
    v_mix5 = Column(String(50))
    v_mix6 = Column(String(50))
    v_position_x = Column(String(50))
    v_he = Column(String(50))
    v_span = Column(String(50))
    v_multi6 = Column(String(50))

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        独胆: save1 \n
        双胆: save2 \n
        三胆: save3 \n
        杀一码: kill1 \n
        杀二码: kill2 \n
        杀三码: kill3 \n
        五码: mix5 \n
        六码: mix6 \n
        定位: position_x \n
        和值: he \n
        跨度: span \n
        组选: multi6 \n
        @param issue: 期号
        @param attribute_name: 属性名称
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x)
                       for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '')
                      for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__,
                       attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            '√' if self.v_save1.find('正确') > -1 else '×',
            '√' if self.v_save2.find('正确') > -1 else '×',
            '√' if self.v_save3.find('正确') > -1 else '×',
            '√' if self.v_kill1.find('正确') > -1 else '×',
            '√' if self.v_kill2.find('正确') > -1 else '×',
            '√' if self.v_kill3.find('正确') > -1 else '×',
            '√' if self.v_mix5.find('正确') > -1 else '×',
            '√' if self.v_mix6.find('正确') > -1 else '×',
            '√' if self.v_position_x.find('正确') > -1 else '×',
            '√' if self.v_he.find('正确') > -1 else '×',
            '√' if self.v_span.find('正确') > -1 else '×',
            '√' if self.v_multi6.find('正确') > -1 else '×'
        ]


class ShiNaJiuWen(Base):
    __tablename__ = 'wx_shinajiuwen'
    _name_ = '十拿九稳'
    issue = Column(Integer, primary_key=True)

    # attributes
    save3 = Column(String(50))  # 胆码
    mix4 = Column(String(50))  # 四码
    mix5 = Column(String(50))  # 五码复式
    mix6 = Column(String(50))  # 六码复式
    mix7 = Column(String(50))  # 七码复式
    position1 = Column(String(50))  # 百位定位推荐
    position2 = Column(String(50))  # 十位定位推荐
    position3 = Column(String(50))  # 个位定位推荐
    result_many = Column(String(500))  # 直选精选
    multi36 = Column(String(500))  # 组选大底

    # verify attribute
    v_save3 = Column(String(50))
    v_mix4 = Column(String(50))
    v_mix5 = Column(String(50))
    v_mix6 = Column(String(50))
    v_mix7 = Column(String(50))
    v_position1 = Column(String(50))
    v_position2 = Column(String(50))
    v_position3 = Column(String(50))
    v_result_many = Column(String(50))
    v_multi36 = Column(String(50))

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        胆码: save3 \n
        四码: mix4 \n
        五码复式: mix5 \n
        六码复式: mix6 \n
        七码复式: mix7 \n
        百位定位推荐: position1 \n
        十位定位推荐: position2 \n
        个位定位推荐: position3 \n
        直选精选: result_many \n
        组选大底: multi36 \n
        @param issue: 期号
        @param attribute_name: 属性名称
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x)
                       for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '')
                      for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表 {self._name_} 属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__,
                       attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            '√' if self.v_save3.find('正确') > -1 else '×',
            '√' if self.v_mix4.find('正确') > -1 else '×',
            '√' if self.v_mix5.find('正确') > -1 else '×',
            '√' if self.v_mix6.find('正确') > -1 else '×',
            '√' if self.v_mix7.find('正确') > -1 else '×',
            '√' if self.v_position1.find('正确') > -1 else '×',
            '√' if self.v_position2.find('正确') > -1 else '×',
            '√' if self.v_position3.find('正确') > -1 else '×',
            '√' if self.v_result_many.find('正确') > -1 else '×',
            '√' if self.v_multi36.find('正确') > -1 else '×'
        ]


class WanCaiLaoTou(Base):
    __tablename__ = 'wx_wancailaotou'
    _name_ = '玩彩老头'
    issue = Column(Integer, primary_key=True)

    # attributes
    kills = Column(String(50))  # 杀码
    position_star = Column(String(50))  # 包星
    save1 = Column(String(50))  # 独胆
    save2 = Column(String(50))  # 双胆
    mix5 = Column(String(50))  # 5码复式
    mix6 = Column(String(50))  # 6码复式
    he = Column(String(50))  # 和值范围
    span = Column(String(50))  # 跨度范围
    multi6 = Column(String(500))  # 组选
    result_many = Column(String(500))  # 单选

    # verify attributes
    v_kills = Column(String(50))
    v_position_star = Column(String(50))
    v_save1 = Column(String(50))
    v_save2 = Column(String(50))
    v_mix5 = Column(String(50))
    v_mix6 = Column(String(50))
    v_he = Column(String(50))
    v_span = Column(String(50))
    v_multi6 = Column(String(50))
    v_result_many = Column(String(50))

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        杀码: kills \n
        包星: position_star \n
        独胆: save1 \n
        双胆: save2 \n
        5码复式: mix5 \n
        6码复式: mix6 \n
        和值范围: he \n
        跨度范围: span \n
        组选: multi6 \n
        单选: result_many \n
        @param issue: 期号
        @param attribute_name: 属性名称
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x)
                       for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '')
                      for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__,
                       attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            '√' if self.v_kills.find('正确') > -1 else '×',
            '√' if self.v_position_star.find('正确') > -1 else '×',
            '√' if self.v_save1.find('正确') > -1 else '×',
            '√' if self.v_save2.find('正确') > -1 else '×',
            '√' if self.v_mix5.find('正确') > -1 else '×',
            '√' if self.v_mix6.find('正确') > -1 else '×',
            '√' if self.v_he.find('正确') > -1 else '×',
            '√' if self.v_span.find('正确') > -1 else '×',
            '√' if self.v_multi6.find('正确') > -1 else '×',
            '√' if self.v_result_many.find('正确') > -1 else '×'
        ]


class XiaoWei(Base):
    __tablename__ = 'wx_xiaowei'
    _name_ = '小微'
    issue = Column(Integer, primary_key=True)
    # attributes
    save1 = Column(String(50))  # 独胆
    save2 = Column(String(50))  # 双胆
    save3 = Column(String(50))  # 三胆
    kill1 = Column(String(50))  # 杀一码
    kill2 = Column(String(50))  # 杀二码
    kill3 = Column(String(50))  # 杀三码
    mix5 = Column(String(50))  # 五码
    mix6 = Column(String(50))  # 六码
    position_x = Column(String(50))  # 定位
    he = Column(String(50))  # 和值
    span = Column(String(50))  # 跨度
    multi6 = Column(String(500))  # 组选

    # verify attributes
    v_save1 = Column(String(50))
    v_save2 = Column(String(50))
    v_save3 = Column(String(50))
    v_kill1 = Column(String(50))
    v_kill2 = Column(String(50))
    v_kill3 = Column(String(50))
    v_mix5 = Column(String(50))
    v_mix6 = Column(String(50))
    v_position_x = Column(String(50))
    v_he = Column(String(50))
    v_span = Column(String(50))
    v_multi6 = Column(String(50))

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        独胆: save1 \n
        双胆: save2 \n
        三胆: save3 \n
        杀一码: kill1 \n
        杀二码: kill2 \n
        杀三码: kill3 \n
        五码: mix5 \n
        六码: mix6 \n
        定位: position_x \n
        和值: he \n
        跨度: span \n
        组选: result_multiple \n
        @param issue: 期号
        @param attribute_name: 属性名称
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x)
                       for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '')
                      for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__,
                       attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            '√' if self.v_save1.find('正确') > -1 else '×',
            '√' if self.v_save2.find('正确') > -1 else '×',
            '√' if self.v_save3.find('正确') > -1 else '×',
            '√' if self.v_kill1.find('正确') > -1 else '×',
            '√' if self.v_kill2.find('正确') > -1 else '×',
            '√' if self.v_kill3.find('正确') > -1 else '×',
            '√' if self.v_mix5.find('正确') > -1 else '×',
            '√' if self.v_mix6.find('正确') > -1 else '×',
            '√' if self.v_position_x.find('正确') > -1 else '×',
            '√' if self.v_he.find('正确') > -1 else '×',
            '√' if self.v_span.find('正确') > -1 else '×',
            '√' if self.v_multi6.find('正确') > -1 else '×'
        ]


class YueYeFeiLong(Base):
    __tablename__ = 'wx_yueyefeilong'
    _name_ = '月夜飞龙'
    issue = Column(Integer, primary_key=True)

    # attributes
    save1 = Column(String(50))  # 独胆
    save2 = Column(String(50))  # 双胆
    save3 = Column(String(50))  # 三胆
    kill1 = Column(String(50))  # 杀一码
    kill2 = Column(String(50))  # 杀二码
    kill3 = Column(String(50))  # 杀三码
    mix5 = Column(String(50))  # 五码
    mix6 = Column(String(50))  # 六码
    position_x = Column(String(50))  # 定位
    he = Column(String(50))  # 和值
    span = Column(String(50))  # 跨度
    multi6 = Column(String(500))  # 组选

    # verify attributes
    v_save1 = Column(String(50))
    v_save2 = Column(String(50))
    v_save3 = Column(String(50))
    v_kill1 = Column(String(50))
    v_kill2 = Column(String(50))
    v_kill3 = Column(String(50))
    v_mix5 = Column(String(50))
    v_mix6 = Column(String(50))
    v_position_x = Column(String(50))
    v_he = Column(String(50))
    v_span = Column(String(50))
    v_multi6 = Column(String(50))

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        独胆: save1 \n
        双胆: save2 \n
        三胆: save3 \n
        杀一码: kill1 \n
        杀二码: kill2 \n
        杀三码: kill3 \n
        五码: mix5 \n
        六码: mix6 \n
        定位: position_x \n
        和值: he \n
        跨度: span \n
        组选: result_multiple \n
        @param issue: 期号
        @param attribute_name: 属性名称
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x)
                       for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '')
                      for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__,
                       attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            '√' if self.v_save1.find('正确') > -1 else '×',
            '√' if self.v_save2.find('正确') > -1 else '×',
            '√' if self.v_save3.find('正确') > -1 else '×',
            '√' if self.v_kill1.find('正确') > -1 else '×',
            '√' if self.v_kill2.find('正确') > -1 else '×',
            '√' if self.v_kill3.find('正确') > -1 else '×',
            '√' if self.v_mix5.find('正确') > -1 else '×',
            '√' if self.v_mix6.find('正确') > -1 else '×',
            '√' if self.v_position_x.find('正确') > -1 else '×',
            '√' if self.v_he.find('正确') > -1 else '×',
            '√' if self.v_span.find('正确') > -1 else '×',
            '√' if self.v_multi6.find('正确') > -1 else '×'
        ]


class ZhouXingXing(Base):
    __tablename__ = 'wx_zhouxingxing'
    _name_ = '周星星'
    issue = Column(Integer, primary_key=True)
    # attributes
    save1 = Column(String(50))  # 独胆
    save2 = Column(String(50))  # 双胆
    save3 = Column(String(50))  # 三胆
    kill1 = Column(String(50))  # 杀一码
    kill2 = Column(String(50))  # 杀二码
    kill3 = Column(String(50))  # 杀三码
    mix5 = Column(String(50))  # 五码
    mix6 = Column(String(50))  # 六码
    position_x = Column(String(50))  # 定位
    he = Column(String(50))  # 和值
    span = Column(String(50))  # 跨度
    multi6 = Column(String(500))  # 组选

    # verify attributes
    v_save1 = Column(String(50))
    v_save2 = Column(String(50))
    v_save3 = Column(String(50))
    v_kill1 = Column(String(50))
    v_kill2 = Column(String(50))
    v_kill3 = Column(String(50))
    v_mix5 = Column(String(50))
    v_mix6 = Column(String(50))
    v_position_x = Column(String(50))
    v_he = Column(String(50))
    v_span = Column(String(50))
    v_multi6 = Column(String(50))

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        独胆: save1 \n
        双胆: save2 \n
        三胆: save3 \n
        杀一码: kill1 \n
        杀二码: kill2 \n
        杀三码: kill3 \n
        五码: mix5 \n
        六码: mix6 \n
        定位: position_x \n
        和值: he \n
        跨度: span \n
        组选: result_multiple \n
        @param issue: 期号
        @param attribute_name: 属性名称
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x)
                       for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '')
                      for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__,
                       attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            '√' if self.v_save1.find('正确') > -1 else '×',
            '√' if self.v_save2.find('正确') > -1 else '×',
            '√' if self.v_save3.find('正确') > -1 else '×',
            '√' if self.v_kill1.find('正确') > -1 else '×',
            '√' if self.v_kill2.find('正确') > -1 else '×',
            '√' if self.v_kill3.find('正确') > -1 else '×',
            '√' if self.v_mix5.find('正确') > -1 else '×',
            '√' if self.v_mix6.find('正确') > -1 else '×',
            '√' if self.v_position_x.find('正确') > -1 else '×',
            '√' if self.v_he.find('正确') > -1 else '×',
            '√' if self.v_span.find('正确') > -1 else '×',
            '√' if self.v_multi6.find('正确') > -1 else '×'
        ]


class ZiYunJian(Base):
    """
    position5_1
    position5_2
    position5_3
    position3_1
    position3_2
    position3_3
    save3
    mix4
    mix5
    multi36
    """
    __tablename__ = 'wx_ziyunjian'
    _name_ = '紫云涧'
    issue = Column(Integer, primary_key=True)

    # attributes
    position5_1 = Column(String(50))  # 555复式 百位
    position5_2 = Column(String(50))  # 555复式 十位
    position5_3 = Column(String(50))  # 555复式 个位
    position3_1 = Column(String(50))  # 333复式 百位
    position3_2 = Column(String(50))  # 333复式 十位
    position3_3 = Column(String(50))  # 333复式 个位
    save3 = Column(String(50))  # 三胆
    mix4 = Column(String(50))  # 四码
    mix5 = Column(String(50))  # 五码
    multi36 = Column(String(500))  # 直,组推荐

    # verify attributes
    v_position5_1 = Column(String(50))
    v_position5_2 = Column(String(50))
    v_position5_3 = Column(String(50))
    v_position3_1 = Column(String(50))
    v_position3_2 = Column(String(50))
    v_position3_3 = Column(String(50))
    v_save3 = Column(String(50))
    v_mix4 = Column(String(50))
    v_mix5 = Column(String(50))
    v_multi36 = Column(String(50))

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        555复式 百位：position5_1    \n
        555复式 十位：position5_2    \n
        555复式 个位：position5_3    \n
        333复式 百位：position3_1    \n
        333复式 十位：position3_2    \n
        333复式 个位：position3_3    \n
        三胆：save3    \n
        四码：mix4  \n
        五码：mix5  \n
        直,组推荐：multi36   \n

        @param issue: 期号 \n
        @param attribute_name: 属性名称 \n
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x) for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '') for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__, attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            '√' if self.v_position5_1.find('正确') > -1 else '×',
            '√' if self.v_position5_2.find('正确') > -1 else '×',
            '√' if self.v_position5_3.find('正确') > -1 else '×',
            '√' if self.v_position3_1.find('正确') > -1 else '×',
            '√' if self.v_position3_2.find('正确') > -1 else '×',
            '√' if self.v_position3_3.find('正确') > -1 else '×',
            '√' if self.v_save3.find('正确') > -1 else '×',
            '√' if self.v_mix4.find('正确') > -1 else '×',
            '√' if self.v_mix5.find('正确') > -1 else '×',
            '√' if self.v_multi36.find('正确') > -1 else '×'
        ]


class AnMei(Base):
    """
    mix7
    group3
    """
    __tablename__ = 'zm_anmei'
    _name_ = '安美'
    issue = Column(Integer, primary_key=True)

    # attributes
    mix7 = Column(String(50))  # 七码 \d{7}
    group3 = Column(String(50))  # 三组 (\d{3})(\d{3})(\d{3})

    # verify attributes
    v_mix7 = Column(String(50))
    v_group3 = Column(String(50))

    @classmethod
    def get_mix7_by_issue(cls, issue_target) -> list:
        sess = get_session_welfare()
        data = sess.query(cls).get(issue_target)
        data_mix_7 = [int(x) for x in data.mix7.split(",")]
        return data_mix_7

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        盈利七码: mix7 \n
        防组选三: group3 \n
        @param issue: 期号 \n
        @param attribute_name: 属性名称 \n
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x) for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '') for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__, attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            self.v_mix7,
            '√' if self.v_group3.find('正确') > -1 else '×'
        ]

    @classmethod
    def get_issue_latest(cls):
        sess = get_session_welfare()
        data = sess.query(cls).all()
        issues = [x.issue for x in data]
        issues.sort()
        return issues[-1]


class BaoBing(Base):
    """
    mix7
    group3
    """
    __tablename__ = 'zm_baobing'
    _name_ = '保兵'
    issue = Column(Integer, primary_key=True)

    # attributes
    mix7 = Column(String(50))  # 七码 \d{7}
    group3 = Column(String(50))  # 三组 (\d{3})(\d{3})(\d{3})

    # verify attributes
    v_mix7 = Column(String(50))
    v_group3 = Column(String(50))

    @classmethod
    def get_mix7_by_issue(cls, issue_target) -> list:
        sess = get_session_welfare()
        data = sess.query(cls).get(issue_target)
        data_mix_7 = [int(x) for x in data.mix7.split(",")]
        return data_mix_7

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        盈利七码: mix7 \n
        防组选三: group3 \n
        @param issue: 期号 \n
        @param attribute_name: 属性名称 \n
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x) for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '') for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__, attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            self.v_mix7,
            '√' if self.v_group3.find('正确') > -1 else '×'
        ]

    @classmethod
    def get_issue_latest(cls):
        sess = get_session_welfare()
        data = sess.query(cls).all()
        issues = [x.issue for x in data]
        issues.sort()
        return issues[-1]


class ChaoDong(Base):
    """
    mix7
    group3
    """
    __tablename__ = 'zm_chaodong'
    _name_ = '超东'
    issue = Column(Integer, primary_key=True)

    # attributes
    mix7 = Column(String(50))  # 七码 \d{7}
    group3 = Column(String(50))  # 三组 (\d{3})(\d{3})(\d{3})

    # verify attributes
    v_mix7 = Column(String(50))
    v_group3 = Column(String(50))

    @classmethod
    def get_mix7_by_issue(cls, issue_target) -> list:
        sess = get_session_welfare()
        data = sess.query(cls).get(issue_target)
        data_mix_7 = [int(x) for x in data.mix7.split(",")]
        return data_mix_7

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        盈利七码: mix7 \n
        防组选三: group3 \n
        @param issue: 期号 \n
        @param attribute_name: 属性名称 \n
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x) for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '') for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__, attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            self.v_mix7,
            '√' if self.v_group3.find('正确') > -1 else '×'
        ]


class ChunChen(Base):
    """
    mix7
    group3
    """
    __tablename__ = 'zm_chunchen'
    _name_ = '春琛'
    issue = Column(Integer, primary_key=True)

    # attributes
    mix7 = Column(String(50))  # 七码 \d{7}
    group3 = Column(String(50))  # 三组 (\d{3})(\d{3})(\d{3})

    # verify attributes
    v_mix7 = Column(String(50))
    v_group3 = Column(String(50))

    @classmethod
    def get_mix7_by_issue(cls, issue_target) -> list:
        sess = get_session_welfare()
        data = sess.query(cls).get(issue_target)
        data_mix_7 = [int(x) for x in data.mix7.split(",")]
        return data_mix_7

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        盈利七码: mix7 \n
        防组选三: group3 \n
        @param issue: 期号 \n
        @param attribute_name: 属性名称 \n
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x) for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '') for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__, attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            self.v_mix7,
            '√' if self.v_group3.find('正确') > -1 else '×'
        ]


class FengLiuBing(Base):
    """
    mix7
    group3
    """
    __tablename__ = 'zm_fengliubing'
    _name_ = '风流冰'
    issue = Column(Integer, primary_key=True)

    # attributes
    mix7 = Column(String(50))  # 七码 \d{7}
    group3 = Column(String(50))  # 三组 (\d{3})(\d{3})(\d{3})

    # verify attributes
    v_mix7 = Column(String(50))
    v_group3 = Column(String(50))

    @classmethod
    def get_mix7_by_issue(cls, issue_target) -> list:
        sess = get_session_welfare()
        data = sess.query(cls).get(issue_target)
        data_mix_7 = [int(x) for x in data.mix7.split(",")]
        return data_mix_7

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        盈利七码: mix7 \n
        防组选三: group3 \n
        @param issue: 期号 \n
        @param attribute_name: 属性名称 \n
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x) for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '') for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__, attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            self.v_mix7,
            '√' if self.v_group3.find('正确') > -1 else '×'
        ]


class JiuJiuChongYang(Base):
    """
    mix7
    group3
    """
    __tablename__ = 'zm_jiujiuchongyang'
    _name_ = '九九重阳'
    issue = Column(Integer, primary_key=True)

    # attributes
    mix7 = Column(String(50))  # 七码 \d{7}
    group3 = Column(String(50))  # 三组 (\d{3})(\d{3})(\d{3})

    # verify attributes
    v_mix7 = Column(String(50))
    v_group3 = Column(String(50))

    @classmethod
    def get_mix7_by_issue(cls, issue_target) -> list:
        sess = get_session_welfare()
        data = sess.query(cls).get(issue_target)
        data_mix_7 = [int(x) for x in data.mix7.split(",")]
        return data_mix_7

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        盈利七码: mix7 \n
        防组选三: group3 \n
        @param issue: 期号 \n
        @param attribute_name: 属性名称 \n
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x) for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '') for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__, attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            self.v_mix7,
            '√' if self.v_group3.find('正确') > -1 else '×'
        ]


class RuYin(Base):
    """
    mix7
    group3
    """
    __tablename__ = 'zm_ruyin'
    _name_ = '汝茵'
    issue = Column(Integer, primary_key=True)

    # attributes
    mix7 = Column(String(50))  # 七码 \d{7}
    group3 = Column(String(50))  # 三组 (\d{3})(\d{3})(\d{3})

    # verify attributes
    v_mix7 = Column(String(50))
    v_group3 = Column(String(50))

    @classmethod
    def get_mix7_by_issue(cls, issue_target) -> list:
        sess = get_session_welfare()
        data = sess.query(cls).get(issue_target)
        data_mix_7 = [int(x) for x in data.mix7.split(",")]
        return data_mix_7

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        盈利七码: mix7 \n
        防组选三: group3 \n
        @param issue: 期号 \n
        @param attribute_name: 属性名称 \n
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x) for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '') for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__, attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            self.v_mix7,
            '√' if self.v_group3.find('正确') > -1 else '×'
        ]


class YiBiao(Base):
    """
    mix7
    group3
    """
    __tablename__ = 'zm_yibiao'
    _name_ = '一彪'
    issue = Column(Integer, primary_key=True)

    # attributes
    mix7 = Column(String(50))  # 七码 \d{7}
    group3 = Column(String(50))  # 三组 (\d{3})(\d{3})(\d{3})

    # verify attributes
    v_mix7 = Column(String(50))
    v_group3 = Column(String(50))

    @classmethod
    def get_mix7_by_issue(cls, issue_target) -> list:
        sess = get_session_welfare()
        data = sess.query(cls).get(issue_target)
        data_mix_7 = [int(x) for x in data.mix7.split(",")]
        return data_mix_7

    def set_attribute(self, issue: int, attribute_name: str, data: str):
        """
        属性名称：\n
        盈利七码: mix7 \n
        防组选三: group3 \n
        @param issue: 期号 \n
        @param attribute_name: 属性名称 \n
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        total_names = [str(x) for x in self.metadata.tables[self.__tablename__].columns]
        attributes = [x.replace(f'{self.__tablename__}.', '') for x in total_names]
        session = get_session_welfare()
        self.issue = issue
        # 选择属性
        if attribute_name == 'issue':
            pass
        elif attribute_name in attributes:
            exec_string = f'self.{attribute_name} = data'
            exec(exec_string)
        else:
            raise Exception(f">>> 数据表《{self._name_}》属性名称错误!!!")
        database_toast(issue, self._name_, self.__tablename__, attribute_name, data)
        session.merge(self)
        session.commit()
        session.close()

    def get_verify(self):
        return [
            self.v_mix7,
            '√' if self.v_group3.find('正确') > -1 else '×'
        ]


class WelfareMiss(Base):
    __tablename__ = 'misses'
    issue = Column(Integer, primary_key=True)
    num1 = Column(Integer, nullable=False)
    num2 = Column(Integer, nullable=False)
    num3 = Column(Integer, nullable=False)
    next1 = Column(Integer)
    next2 = Column(Integer)
    next3 = Column(Integer)
    miss0 = Column(Integer)
    miss1 = Column(Integer)
    miss2 = Column(Integer)
    miss3 = Column(Integer)
    miss4 = Column(Integer)
    miss5 = Column(Integer)
    miss6 = Column(Integer)
    miss7 = Column(Integer)
    miss8 = Column(Integer)
    miss9 = Column(Integer)

    def __init__(self, issue, n1, n2, n3) -> None:
        super().__init__()
        self.issue = issue
        self.num1 = n1
        self.num2 = n2
        self.num3 = n3

    def __str__(self):
        p0 = f'i: {self.issue}\nnumbers: {self.num1}-{self.num2}-{self.num3}\n'
        p1 = f'y  next: {self.next1}-{self.next2}-{self.next3}\n'
        p2 = f'm i s s: {self.miss0}-{self.miss1}-{self.miss2}-{self.miss3}-'
        p3 = f'{self.miss4}-{self.miss5}-{self.miss6}-{self.miss7}-'
        p4 = f'{self.miss8}-{self.miss9}'
        return p0 + p1 + p2 + p3 + p4

    @classmethod
    def get_misses(cls):
        session = get_session_welfare()
        data = session.query(cls).all()
        result = {}
        for t in data:
            result[t.issue] = [
                t.miss0,
                t.miss1,
                t.miss2,
                t.miss3,
                t.miss4,
                t.miss5,
                t.miss6,
                t.miss7,
                t.miss8,
                t.miss9
            ]
        return result

    @classmethod
    def get_numbers(cls):
        """
        [[issue, num1, num2, num3],...]
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[x.issue, x.num1, x.num2, x.num3] for x in data]
        return result

    @classmethod
    def get_number_and_next(cls):
        """
        [[issue, num1, num2, num3, next1, next2, next3],...]
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[x.issue, x.num1, x.num2, x.num3, x.next1, x.next2, x.next3] for x in data]
        return result

    @classmethod
    def get_all(cls):
        """
        获取所有的数据
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[
            x.issue,
            x.num1,
            x.num2,
            x.num3,
            x.next1,
            x.next2,
            x.next3,
            x.miss0,
            x.miss1,
            x.miss2,
            x.miss3,
            x.miss4,
            x.miss5,
            x.miss6,
            x.miss7,
            x.miss8,
            x.miss9
        ] for x in data]
        return result

    @classmethod
    def get_issues(cls):
        """get issues"""
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [x.issue for x in data]
        result.sort()
        return result


class WelfareExpertFSS(Base):
    """
    issue
    name
    issue_name
    save
    v_save
    """
    __tablename__ = 'fss_experts'
    issue_name = Column(String(50), primary_key=True)  # 期号_专家名

    # attributes
    issue = Column(String(50))  # 期号
    name = Column(String(50))  # 专家名
    save = Column(String(50))  # 组选

    # verify attributes
    v_save = Column(String(50))  # 组选成绩

    @classmethod
    def set_attributes_except_v(cls, issue_name: str, issue: str, name: str, save: str):
        """set_attributes
        @param issue_name: 期号_专家名 \n
        @param data: 属性的数据
        """
        # create instance
        session = get_session_welfare()
        ins = cls()
        ins.issue_name = issue_name
        ins.issue = issue
        ins.name = name
        ins.save = save
        print(f">>> 合并数据成功，期号_专家名：{issue_name}，value: {save}")
        session.merge(ins)
        session.commit()
        session.close()

    @classmethod
    def set_attribute(cls, issue_name: str, attribute_name: str, data: str):
        """set_attribute
        @param issue: 期号 \n
        @param attribute_name: 属性名称 \n
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        # total_names = [str(x) for x in cls.metadata.tables[cls.__tablename__].columns]
        # attributes = [x.replace(f'{cls.__tablename__}.', '') for x in total_names]
        session = get_session_welfare()
        ins = cls()
        ins.issue_name = issue_name
        # 选择属性
        if attribute_name == 'issue_name':
            pass
        elif attribute_name == 'issue':
            ins.issue = data
        elif attribute_name == 'name':
            ins.name = data
        elif attribute_name == 'save':
            ins.save = data
        elif attribute_name == 'v_save':
            ins.v_save = data
        else:
            raise Exception(f">>> 数据表《{cls._name_}》属性名称错误!!!")
        database_toast(issue_name, cls.__tablename__, attribute_name,  data)
        session.merge(ins)
        session.commit()
        session.close()

    @classmethod
    def get_verify(cls):
        return cls.v_save


class WelfareExpertOTT(Base):
    """
    issue
    name
    issue_name
    save
    v_save
    """
    __tablename__ = 'ott_experts'
    issue_name = Column(String(50), primary_key=True)  # 期号_专家名

    # attributes
    issue = Column(String(50))  # 期号
    name = Column(String(50))  # 专家名
    save = Column(String(50))  # 组选

    # verify attributes
    v_save = Column(String(50))  # 组选成绩

    @classmethod
    def set_attributes_except_v(cls, issue_name: str, issue: str, name: str, save: str):
        """set_attributes
        @param issue_name: 期号_专家名 \n
        @param data: 属性的数据
        """
        # create instance
        session = get_session_welfare()
        ins = cls()
        ins.issue_name = issue_name
        ins.issue = issue
        ins.name = name
        ins.save = save
        print(f">>> 合并数据成功，期号_专家名：{issue_name}，value: {save}")
        session.merge(ins)
        session.commit()
        session.close()

    @classmethod
    def set_attribute(cls, issue_name: str, attribute_name: str, data: str):
        """set_attribute
        @param issue: 期号 \n
        @param attribute_name: 属性名称 \n
        @param data: 属性的数据
        """
        # 获取表的字段名称集合
        # total_names = [str(x) for x in cls.metadata.tables[cls.__tablename__].columns]
        # attributes = [x.replace(f'{cls.__tablename__}.', '') for x in total_names]
        session = get_session_welfare()
        ins = cls()
        ins.issue_name = issue_name
        # 选择属性
        if attribute_name == 'issue_name':
            pass
        elif attribute_name == 'issue':
            ins.issue = data
        elif attribute_name == 'name':
            ins.name = data
        elif attribute_name == 'save':
            ins.save = data
        elif attribute_name == 'v_save':
            ins.v_save = data
        else:
            raise Exception(f">>> 数据表《{cls._name_}》属性名称错误!!!")
        database_toast(issue_name, cls.__tablename__, attribute_name,  data)
        session.merge(ins)
        session.commit()
        session.close()

    @classmethod
    def get_verify(cls):
        return cls.v_save


class WelfareVerify(Base):
    __tablename__ = "verifies"

    inumabc = Column(String(50), primary_key=True)
    issue = Column(Integer)
    num = Column(Integer)
    abc = Column(String(50))
    result = Column(String(50))
    score = Column(Float)
    num1 = Column(Integer)
    num2 = Column(Integer)
    num3 = Column(Integer)
    verify = Column(String(50))

    @classmethod
    def get_result_score_or_false(cls, issue_num_abc: str):
        with get_session_welfare() as sess:
            # sess = get_session_welfare()
            data = sess.query(cls).get(issue_num_abc)
            if data:
                return {'label': data.result, 'predicts': data.score}
            else:
                return False

    def __init__(self, inumabc, issue, num, abc, result, score):
        super().__init__()
        self.inumabc = inumabc
        self.issue = issue
        self.num = num
        self.abc = abc
        self.result = result
        self.score = score

    @classmethod
    def get_model_score(cls, path_json: str) -> dict:
        """
        检查表 verifies 最后5期的数据，得出所有模型的得分，并写入指定的json文件，并返回结果
        base                         s1     1
        verify == 'y' & 不包含开奖号  s2     1
        verify == 'y' & 又包含开奖号  s3     2
        verify == 'n'                       0
        """
        s1 = 1
        s2 = 1
        s3 = 2

        sess = get_session_welfare()
        # 获取最后5期的期号
        num_all = sess.query(WelfareNumber).order_by(WelfareNumber.issue).all()
        num_last5 = num_all[-5:]
        issue_begin = num_last5[0].issue

        # 获取最后5期的 verifies 表数据
        data_verifies = sess.query(cls).filter(cls.issue >= issue_begin).all()
        dict_verifies = {x.inumabc: x for x in data_verifies}
        result = dict()

        # 循环模型名称
        for num in range(10):
            for p1 in range(10):
                for p2 in range(10):
                    for p3 in range(10):
                        num_a_b_c = f'{num}{p1}{p2}{p3}'
                        result[num_a_b_c] = s1
                        # 循环最后5期的数据
                        for n in num_last5:
                            i = n.issue
                            nums = [n.num1, n.num2, n.num3]
                            i_num_a_b_c = f'{i}{num_a_b_c}'
                            ins = dict_verifies.get(i_num_a_b_c)
                            if ins.verify == 'y':
                                if ins.num in nums:
                                    result[num_a_b_c] = result[num_a_b_c] + s3
                                else:
                                    result[num_a_b_c] = result[num_a_b_c] + s2
        # result
        with open(path_json, 'w') as file_write:
            json.dump(result, file_write)
        print(">>> json result has been written at:", path_json)
        return result

    @classmethod
    def add_score(cls, inumabc, issue, num, abc, result, score):
        sess = get_session_welfare()
        ins = cls(inumabc, issue, num, abc, result, score)
        issues_all = WelfareNumber.get_issues()
        if issue in issues_all:
            numbers = WelfareNumber.get_one(issue)
            if int(num) in numbers[1:]:
                if result == 'y':
                    ins.verify = 'y'
                else:
                    ins.verify = 'n'
            else:
                if result == 'y':
                    ins.verify = 'n'
                else:
                    ins.verify = 'y'
        else:
            ins.verify = None
        sess.merge(ins)
        sess.commit()
        sess.close()
        print(
            f">>> {cls.__tablename__}: add score: inumabc: {inumabc}, issue: {issue}, num: {num}, abc: {abc}, result: {result}, score: {score}, verify: {ins.verify}")

    @classmethod
    def whether_needs_retrained(cls, num_abc: str, last_num: int, min_right: int):
        """检查模型最后几期的准确率，判断是否合格

        Args:
            num_abc (str): num + abc [1008]
            last_num (int): 检查最后几期
            min_right (int): 最小正确数

        Returns:
            [type]: [description]
        """
        # 检查模型最后几期的准确率，判断是否合格
        if min_right > last_num:
            raise Exception(">>> ERROR PARAM: min_right > last_num")
        if len(num_abc) != 4:
            raise Exception(">>> ERROR PARAM: num_abc", num_abc)
        num_abc = str(num_abc)
        whether_train = True
        num = num_abc[0]
        sess = get_session_welfare()
        issue_all = WelfareNumber.get_issues()
        issue_last = issue_all[-last_num:]
        coll_verify = []
        coll_verify_all = []
        for i_target in issue_last:
            i_num_abc = f'{i_target}{num_abc}'
            v_ins = sess.query(cls).get(i_num_abc)
            coll_verify.append(v_ins.verify)
            temp_dict = {
                'num123': f'{v_ins.num1}{v_ins.num2}{v_ins.num3}',
                'result': v_ins.result,
                'verify': v_ins.verify
            }
            coll_verify_all.append(temp_dict)
            print(f'model: {num_abc}, result: {temp_dict}')

        # 检查 y 的数量
        if coll_verify.count('y') >= min_right:
            whether_train = False

            # 检查 出号必y
            for one_coll in coll_verify_all:
                if one_coll['num123'].find(str(num)) > -1:
                    if one_coll['verify'] == 'n':
                        whether_train = True

        print(f">>> whether_needs_retrained: {num_abc} - {whether_train}")
        return whether_train


class WelfareVerifyAbstract(Base):
    __abstract__ = True

    inumabc = Column(String(50), primary_key=True)
    issue = Column(Integer)
    num = Column(Integer)
    abc = Column(String(50))
    result = Column(String(50))
    score = Column(Float)
    num1 = Column(Integer)
    num2 = Column(Integer)
    num3 = Column(Integer)
    verify = Column(String(50))

    @classmethod
    def get_result_score_or_false(cls, issue_num_abc: str):
        with get_session_welfare() as sess:
            # sess = get_session_welfare()
            data = sess.query(cls).get(issue_num_abc)
            if data:
                return {'label': data.result, 'predicts': data.score}
            else:
                return False

    @classmethod
    def get_model_score(cls, path_json: str) -> dict:
        """
        检查表 verifies 最后5期的数据，得出所有模型的得分，并写入指定的json文件，并返回结果
        base                         s1     1
        verify == 'y' & 不包含开奖号  s2     1
        verify == 'y' & 又包含开奖号  s3     2
        verify == 'n'                       0
        """

        channel = cls.__tablename__[-1]
        s1 = 1
        s2 = 1
        s3 = 2

        sess = get_session_welfare()
        # 获取最后5期的期号
        num_all = sess.query(WelfareNumber).order_by(WelfareNumber.issue).all()
        num_last5 = num_all[-5:]
        issue_begin = num_last5[0].issue

        # 获取最后5期的 verifies 表数据
        data_verifies = sess.query(cls).filter(cls.issue >= issue_begin).all()
        dict_verifies = {x.inumabc: x for x in data_verifies}
        result = dict()

        # 循环模型名称
        for num in range(10):
            for p1 in range(6):
                for p2 in range(6):
                    for p3 in range(6):
                        num_a_b_c = f'{num}{p1}{p2}{p3}'
                        result[num_a_b_c] = s1
                        # 循环最后5期的数据
                        for n in num_last5:
                            i = n.issue
                            nums = {'a': n.num1, 'b': n.num2, 'c': n.num3}.get(channel)
                            i_num_a_b_c = f'{i}{num_a_b_c}'
                            ins = dict_verifies.get(i_num_a_b_c)
                            if ins.verify == 'y':
                                if ins.num == nums:
                                    result[num_a_b_c] = result[num_a_b_c] + s3
                                else:
                                    result[num_a_b_c] = result[num_a_b_c] + s2
        # result
        with open(path_json, 'w') as file_write:
            json.dump(result, file_write)
        print(">>> json result has been written at:", path_json)
        return result

    @classmethod
    def add_score(cls, inumabc, issue: int, num, abc, result, score: float):
        channel = cls.__tablename__[-1]
        if channel not in ['a', 'b', 'c']:
            raise Exception(f">>> class: {cls.__class__.__name__}, method: add_score")
        sess = get_session_welfare()
        ins = cls(inumabc, issue, num, abc, result, score)
        issues_all = WelfareNumber.get_issues()
        if int(issue) in issues_all:
            ins.num1 = sess.query(WelfareNumber).get(issue).num1
            ins.num2 = sess.query(WelfareNumber).get(issue).num2
            ins.num3 = sess.query(WelfareNumber).get(issue).num3
            number = {'a': ins.num1, 'b': ins.num2, 'c': ins.num3}.get(channel)
            if int(num) == number:
                if result == 'y':
                    ins.verify = 'y'
                else:
                    ins.verify = 'n'
            else:
                if result == 'y':
                    ins.verify = 'n'
                else:
                    ins.verify = 'y'
        else:
            ins.verify = None
        sess.merge(ins)
        sess.commit()
        sess.close()
        print(
            f">>> {cls.__tablename__} add score: inumabc: {inumabc}, issue: {issue}, num: {num}, abc: {abc}, result: {result}, score: {score}, verify: {ins.verify}")

    @classmethod
    def whether_needs_retrained(cls, num_abc: str, last_num: int, min_right: int):
        """检查模型最后几期的准确率，判断是否合格

        Args:
            num_abc (str): num + abc [1008]
            last_num (int): 检查最后几期
            min_right (int): 最小正确数

        Returns:
            [type]: [description]
        """
        # 检查模型最后几期的准确率，判断是否合格
        if min_right > last_num:
            raise Exception(">>> ERROR PARAM: min_right > last_num")
        if len(num_abc) != 4:
            raise Exception(">>> ERROR PARAM: num_abc", num_abc)
        num_abc = str(num_abc)
        whether_train = True
        num = num_abc[0]
        sess = get_session_welfare()
        issue_all = WelfareNumber.get_issues()
        issue_last = issue_all[-last_num:]
        coll_verify = []
        coll_verify_all = []
        for i_target in issue_last:
            i_num_abc = f'{i_target}{num_abc}'
            # print("i_num_abc: ", i_num_abc)
            v_ins = sess.query(cls).get(i_num_abc)
            coll_verify.append(v_ins.verify)
            if cls.__tablename__ == 'verifya':
                temp_num123 = str(v_ins.num1)
            elif cls.__tablename__ == 'verifyb':
                temp_num123 = str(v_ins.num2)
            elif cls.__tablename__ == 'verifyc':
                temp_num123 = str(v_ins.num3)
            else:
                raise(">>> ERROR TABLENAME")
            temp_dict = {
                'num123': temp_num123,
                'result': v_ins.result,
                'verify': v_ins.verify
            }
            coll_verify_all.append(temp_dict)
            print(f'model: {num_abc}, result: {temp_dict}')

        # 检查 y 的数量
        if coll_verify.count('y') >= min_right:
            whether_train = False

            # 检查 出号必y
            for one_coll in coll_verify_all:
                if one_coll['num123'] == str(num):
                    if one_coll['verify'] == 'n':
                        whether_train = True

        print(f">>> Table: {cls.__tablename__}  whether_needs_retrained: {num_abc} - {whether_train}")
        return whether_train


class WelfareVerifyA(WelfareVerifyAbstract):
    __tablename__ = "verifya"

    def __init__(self, inumabc, issue, num, abc, result, score):
        super().__init__()
        self.inumabc = inumabc
        self.issue = issue
        self.num = num
        self.abc = abc
        self.result = result
        self.score = score


class WelfareVerifyB(WelfareVerifyAbstract):
    __tablename__ = "verifyb"

    def __init__(self, inumabc, issue, num, abc, result, score):
        super().__init__()
        self.inumabc = inumabc
        self.issue = issue
        self.num = num
        self.abc = abc
        self.result = result
        self.score = score


class WelfareVerifyC(WelfareVerifyAbstract):
    __tablename__ = "verifyc"

    def __init__(self, inumabc, issue, num, abc, result, score):
        super().__init__()
        self.inumabc = inumabc
        self.issue = issue
        self.num = num
        self.abc = abc
        self.result = result
        self.score = score


class WelfareFollowX(Base):
    __abstract__ = True

    issue = Column(Integer, primary_key=True)
    num = Column(Integer, nullable=False)
    next1 = Column(Integer)
    next2 = Column(Integer)
    next3 = Column(Integer)
    f0 = Column(Integer)
    f1 = Column(Integer)
    f2 = Column(Integer)
    f3 = Column(Integer)
    f4 = Column(Integer)
    f5 = Column(Integer)
    f6 = Column(Integer)
    f7 = Column(Integer)
    f8 = Column(Integer)
    f9 = Column(Integer)
    c0 = Column(Float)
    c1 = Column(Float)
    c2 = Column(Float)
    c3 = Column(Float)
    c4 = Column(Float)
    c5 = Column(Float)
    c6 = Column(Float)
    c7 = Column(Float)
    c8 = Column(Float)
    c9 = Column(Float)

    # def __init__(self, issue, num) -> None:
    #     super().__init__()
    #     self.issue = issue
    #     self.num = num

    @classmethod
    def get_follow_09(cls):
        session = get_session_welfare()
        data = session.query(cls).all()
        result = {}
        for t in data:
            result[t.issue] = [t.f0, t.f1, t.f2, t.f3, t.f4, t.f5, t.f6, t.f7, t.f8, t.f9]
        return result

    @classmethod
    def get_follow_change_09(cls):
        session = get_session_welfare()
        data = session.query(cls).all()
        result = {}
        for t in data:
            result[t.issue] = [t.f0, t.f1, t.f2, t.f3, t.f4, t.f5, t.f6, t.f7, t.f8,
                               t.f9, t.c0, t.c1, t.c2, t.c3, t.c4, t.c5, t.c6, t.c7, t.c8, t.c9]
        return result

    @classmethod
    def get_nums(cls):
        """
        [[issue, num],...]
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[x.issue, x.num] for x in data]
        return result

    @classmethod
    def get_number_and_next(cls):
        """
        [[issue, num, next1],...]
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[x.issue, x.num, x.next1] for x in data]
        return result

    @classmethod
    def get_all(cls):
        """
        获取所有的数据
        """
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [[
            x.issue,
            x.num,
            x.f0,
            x.f1,
            x.f2,
            x.f3,
            x.f4,
            x.f5,
            x.f6,
            x.f7,
            x.f8,
            x.f9,
            x.c0,
            x.c1,
            x.c2,
            x.c3,
            x.c4,
            x.c5,
            x.c6,
            x.c7,
            x.c8,
            x.c9
        ] for x in data]
        return result

    @classmethod
    def get_issues(cls):
        """get issues"""
        session = get_session_welfare()
        data = session.query(cls).all()
        session.close()
        result = [x.issue for x in data]
        result.sort()
        return result


class WelfareFollowA(WelfareFollowX):
    __tablename__ = 'followa'

    def __init__(self, issue, num) -> None:
        super().__init__()
        self.issue = issue
        self.num = num


class WelfareFollowB(WelfareFollowX):
    __tablename__ = 'followb'

    def __init__(self, issue, num) -> None:
        super().__init__()
        self.issue = issue
        self.num = num


class WelfareFollowC(WelfareFollowX):
    __tablename__ = 'followc'

    def __init__(self, issue, num) -> None:
        super().__init__()
        self.issue = issue
        self.num = num


if __name__ == "__main__":
    # WelfareVerify.add_score('20212882945', 2021288, 2, '945', 'y', 0.49)
    # print(WelfareNumber.get_next3_issues(2021287))
    # generate tables
    # engine = create_engine("mysql+pymysql://root:Wangchenyu2012@localhost:3306/sd")
    # Base.metadata.create_all(engine)
    pass
