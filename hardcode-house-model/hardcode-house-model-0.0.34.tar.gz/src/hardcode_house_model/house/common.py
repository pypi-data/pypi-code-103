

from hardcode_house_model.util.mongo_mixin import MongoMixin
from mongo_driver import Document
from mongo_driver.fields import (BooleanField, DateTimeField, EmbeddedDocument,
                                 EmbeddedDocumentField, FloatField,
                                 StringField)


class HouseProperty(EmbeddedDocument, MongoMixin):
    house_type = StringField()      # 房屋户型
    floor = StringField()           # 所在楼层
    builtup_area = StringField()     # 建筑面积
    house_structure = StringField() # 户型结构
    usable_area = StringField()      # 套内面积
    building_type = StringField()   # 建筑类型
    orientation = StringField()     # 房屋朝向
    building_structure = StringField() # 建筑结构
    decoration = StringField()      # 装修情况
    lift_house_ratio = StringField()   # 梯户比例
    has_lift = BooleanField()       # 配备电梯


class TransactionProperty(EmbeddedDocument, MongoMixin):
    listing_time = DateTimeField()   # 挂牌时间
    transaction_type = StringField() # 交易属性
    last_transaction_time = DateTimeField() # 上次交易
    house_usage = StringField()      # 房屋用途
    hold_time = StringField()        # 房屋持有年限
    property_right = StringField()   # 产权所属
    mortgage = StringField()         # 抵押信息
    ownership_certificate = StringField() # 房本配备pass


class GeographicCoordinate(EmbeddedDocument, MongoMixin):
    latitude = FloatField()
    longitude = FloatField()
    altitude = FloatField()

    def __eq__(self, other):
        factor = 100000
        return int(self.latitude * factor) == int(other.latitude * factor) and int(self.longitude * factor) == int(other.longitude * factor)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        factor = 100000
        return hash((int(self.latitude * factor), int(self.longitude * factor)))


class HouseLocation(EmbeddedDocument, MongoMixin):
    city = StringField()
    district = StringField()
    street = StringField()
    geographic_coordinate = EmbeddedDocumentField(GeographicCoordinate)


class Transaction(EmbeddedDocument, MongoMixin):
    unit_price = FloatField()
    total_price = FloatField()
    deal_date = DateTimeField()


class HouseQuotation(EmbeddedDocument, MongoMixin):
    total_price = FloatField(required=True)
    unit_price = FloatField(required=True)
