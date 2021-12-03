import boto3
import datetime
import logging
import uuid
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import Decimal
from ..utils import mask_fields_in_data

logger = logging.getLogger('microgue')


class DatabaseConnectionFailed(Exception): pass
class DeleteFailed(Exception): pass
class GetFailed(Exception): pass
class ItemAlreadyExists(Exception): pass
class MissingKey(Exception): pass
class UpdateFailed(Exception): pass


class AbstractModel:
    """
    table_name: name of table in dynamodb
    pk: partion key of the table - defaulted to id
    auto_generate_pk: auto generate the pk value using uuid
    sk: sort key for the partition key of the table - defaulted to None
    auto_generate_sk: auto generate the pk value using uuid
    indexes: defines all indexes on your table
        local secondary indexes (lsi) do no require the pk to be defined
        global secondary indexes (gsi) do not require the sk to be defined
        {
            "example_index-index": {
                "pk": "example_index_partition_key",
                "sk": "example_index_sort_key"
            }
        }
    mask_attributes: list of attributes to maske when logging
    """
    table_name = ''

    pk = 'id'
    auto_generate_pk = True

    sk = None
    auto_generate_sk = True

    indexes = {}

    mask_attributes = []

    def __init__(self, *args, **kwargs):
        try:
            database = boto3.resource('dynamodb')
            self.table = database.Table(self.table_name)
        except Exception as e:
            logger.error("########## {} Error".format(self.__class__.__name__))
            logger.error("{}: {}".format(e.__class__.__name__, str(e)))
            raise DatabaseConnectionFailed(str(e))

        super().__init__(*args, **kwargs)

    def get(self, pk_value, sk_value=None):
        logger.debug("########## {} Get ##########".format(self.__class__.__name__))
        logger.debug("{}: {}".format(self.pk, pk_value))
        if self.sk:
            logger.debug("{}: {}".format(self.sk, sk_value))

        # create key based on presence of pk and sk
        key = {self.pk: pk_value}
        if self.sk:
            key[self.sk] = sk_value

        try:
            item = self.table.get_item(Key=key)['Item']
        except Exception as e:
            logger.debug("########## {} Get Failed".format(self.__class__.__name__))
            logger.debug("{}: {}".format(e.__class__.__name__, str(e)))
            raise GetFailed('failed to get item')

        logger.debug("return: {}".format(mask_fields_in_data(item, self.mask_attributes)))

        return self.__replace_decimals(item)

    def insert(self, item):
        item = item.copy()
        logger.debug("########## {} Insert ##########".format(self.__class__.__name__))
        logger.debug("item: {}".format(mask_fields_in_data(item, self.mask_attributes)))

        # check if pk should be generated or if an error should be raise
        if item.get(self.pk) is None:
            if self.auto_generate_pk:
                item[self.pk] = str(uuid.uuid4())
            else:
                raise MissingKey('missing key: {}'.format(self.pk))

        # check if sk should be generated or if an error should be raise
        if self.sk and item.get(self.sk) is None:
            if self.auto_generate_pk:
                item[self.sk] = str(uuid.uuid4())
            else:
                raise MissingKey('missing key: {}'.format(self.sk))

        # add created on to item
        item['created_on'] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # create condition expression to ensure uniqueness based on pk and sk
        condition_expression = 'attribute_not_exists({})'.format(self.pk)
        if self.sk:
            condition_expression += ' AND attribute_not_exists({})'.format(self.sk)

        try:
            # convert floats to decimals for sending to dynamodb
            self.table.put_item(
                Item=self.__replace_floats(item),
                ConditionExpression=condition_expression
            )
        except Exception as e:
            logger.error("########## {} Insert Error".format(self.__class__.__name__))
            logger.error("{}: {}".format(e.__class__.__name__, str(e)))
            if self.sk:
                error = "{} and {} key combo ({} and {}) already exists".format(self.pk, self.sk, item[self.pk], item[self.sk])
            else:
                error = "{} ({}) already exists".format(self.pk, item[self.pk])
            raise ItemAlreadyExists(error)

        logger.debug("return: {}".format(mask_fields_in_data(item, self.mask_attributes)))

        return self.__replace_decimals(item)

    def update(self, updated_item):
        updated_item = updated_item.copy()
        logger.debug("########## {} Update ##########".format(self.__class__.__name__))
        logger.debug("updated_item: {}".format(mask_fields_in_data(updated_item, self.mask_attributes)))

        # convert floats to decimals for sending to dynamodb
        updated_item = self.__replace_floats(updated_item)

        # verify the pk exists
        if self.pk and not updated_item.get(self.pk):
            raise MissingKey('missing key: {}'.format(self.pk))

        # verify the sk exists if one is required
        if self.sk and not updated_item.get(self.sk):
            raise MissingKey('missing key: {}'.format(self.sk))

        # add updated on to item
        updated_item['updated_on'] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # create key based on presence of pk and sk
        pk_value = updated_item.pop(self.pk)
        key = {self.pk: pk_value}
        if self.sk:
            key[self.sk] = updated_item.pop(self.sk)

        # generage the update expression and the expression attribute values
        update_expressions = []
        expression_attribute_values = {}
        for k, v in updated_item.items():
            update_expressions.append("{} = :{}".format(k, k))
            expression_attribute_values[":{}".format(k)] = updated_item[k]

        # run the update
        try:
            item = self.table.update_item(
                Key=key,
                UpdateExpression='set {}'.format(', '.join(update_expressions)),
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )['Attributes']
        except Exception as e:
            logger.debug("########## {} Update Failed".format(self.__class__.__name__))
            logger.debug("{}: {}".format(e.__class__.__name__, str(e)))
            raise UpdateFailed('failed to update item')

        logger.debug("return: {}".format(mask_fields_in_data(item, self.mask_attributes)))

        return self.__replace_decimals(item)

    def delete(self, pk_value, sk_value=None):
        logger.debug("########## {} Delete ##########".format(self.__class__.__name__))
        logger.debug("{}: {}".format(self.pk, pk_value))
        if self.sk:
            logger.debug("{}: {}".format(self.sk, sk_value))

        # create key based on presence of pk and sk
        key = {self.pk: pk_value}
        if self.sk:
            key[self.sk] = sk_value

        try:
            self.table.delete_item(Key=key)
        except Exception as e:
            logger.debug("########## {} Delete Failed".format(self.__class__.__name__))
            logger.debug("{}: {}".format(e.__class__.__name__, str(e)))
            raise DeleteFailed('failed to delete item')

        return True

    def get_all_by_pk(self, pk_value):
        logger.debug("########## {} Get All By PK ##########".format(self.__class__.__name__))
        logger.debug("{}: {}".format(self.pk, pk_value))
        return self.query(Key(self.pk).eq(pk_value))

    def get_all_by_index(self, index, pk_value, sk_value=None):
        pk, sk = self._get_pk_and_sk_for_index(index)
        logger.debug("########## {} - Get All By Index ##########".format(self.__class__.__name__))
        logger.debug("index: {}".format(index))
        logger.debug("{}: {}".format(pk, pk_value))
        if sk and sk_value:
            logger.debug("{}: {}".format(sk, sk_value))

        # create key condition expression based on presence of pk and sk for the index
        key_condition_expression = Key(pk).eq(pk_value)
        if sk and sk_value:
            key_condition_expression = key_condition_expression & Key(sk).eq(sk_value)

        return self.query(key_condition_expression, index)

    def query(self, key_condition_expression, index=None):
        if index:
            response = self.table.query(
                IndexName=index,
                KeyConditionExpression=key_condition_expression
            )
        else:
            response = self.table.query(
                KeyConditionExpression=key_condition_expression
            )

        items = response.get('Items')
        while 'LastEvaluatedKey' in response:
            response = self.table.query(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.append(response['Items'])

        return self.__replace_decimals(items)

    def _get_pk_and_sk_for_index(self, index):
        pk = self.indexes.get(index, {}).get('pk', self.pk)
        sk = self.indexes.get(index, {}).get('sk', None)
        return pk, sk

    def __replace_floats(self, item):
        # convert floats to Decimals when sending data to dynamodb
        if isinstance(item, list):
            for index in range(len(item)):
                item[index] = self.__replace_floats(item[index])
            return item
        elif isinstance(item, dict):
            for key in item.keys():
                item[key] = self.__replace_floats(item[key])
            return item
        elif isinstance(item, float):
            return Decimal(str(item))
        else:
            return item

    def __replace_decimals(self, item):
        # convert Decimals to floats or ints when receiving data from dynamodb
        if isinstance(item, list):
            for index in range(len(item)):
                item[index] = self.__replace_decimals(item[index])
            return item
        elif isinstance(item, dict):
            for key in item.keys():
                item[key] = self.__replace_decimals(item[key])
            return item
        elif isinstance(item, Decimal):
            if item % 1 == 0:
                return int(item)
            else:
                return float(item)
        else:
            return item
