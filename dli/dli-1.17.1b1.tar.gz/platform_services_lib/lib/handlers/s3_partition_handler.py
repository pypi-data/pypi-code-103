import logging
import operator
import re
from typing import Optional, List
from dateutil.parser import isoparse

from ..services.exceptions import UnableToParsePartition

logger = logging.getLogger(__name__)

class PartitionOperatorValueModel:
    # todo - remove this model, its only used then jettisoned for the as_dict result
    """
    Field that serializes to a title case string and deserializes to a lower case string.
    """
    _re_match = re.compile(
        r'^([\sa-zA-z0-9_-]+)'
        '(<=|<|=|>|>=|!=)((?!<=|<|=|>|>=|!=)'
        r'[\sa-zA-z0-9_-]+)$'
    )

    def __init__(self, val):
        matches = PartitionOperatorValueModel._re_match.match(val)
        self.valid = True
        if not matches or len(matches.groups()) != 3:
            self.valid = False
            raise ValueError(
                f"Requested partition is invalid: {val}. Partition arguments "
                f"must be alphanumeric separated by an operator, and must "
                f"not be wrapped in special characters like single or double "
                f"quotations."
            )
        else:
            self.partition, self.operator, self.value = matches.groups()

    def as_dict(self):
        if self.valid:
            return {
                'partition': str(self.partition),
                'operator': str(self.operator),
                'value': str(self.value)
            }

        return None


def _operator_lookup(op):
    return {
        '<': operator.lt,
        '>': operator.gt,
        '=': operator.eq,
        '<=': operator.le,
        '>=': operator.ge,
        '!=': operator.ne
    }[op]


def _eval_logical(oper, field, val):
    return _operator_lookup(oper)(field, val)


def get_partitions_in_filepath(filepath: str):
    splits = filepath.split("/")
    # n.b. kind of unsafe as need specifically two elements to each sub-list else will break
    return [x.split("=") for x in splits if "=" in x]


def meets_partition_params(
        file_path: str, query_partitions: Optional[List]
):
    if query_partitions is None:
        return True

    found_partitions = dict(get_partitions_in_filepath(file_path))

    filtered = [
        x for x in query_partitions
        if x['partition'] in found_partitions
    ]

    # Example:
    # found_p = dict[(k,v), (k1,v1)] = k:v, k1:v1
    # query_p = [{'partition':'date', 'operator':'<', 'value':'20190102'}]

    for filterable in filtered:
        field = filterable['partition'].strip()
        compare_val = found_partitions[field]
        op = filterable['operator'].strip()
        filter_value = filterable['value'].strip()

        if field.startswith('as_of_'):
            try:
                filter_value_date = isoparse(filter_value)
            except ValueError as e:
                # This means a user has given an invalid date i.e. not in
                # the correct ISO 8601 format for Python datetime.
                raise UnableToParsePartition(
                    f'Was unable to parse the filter value provided: '
                    f'{filter_value} file_path: {file_path}'
                ) from e

            try:
                compare_val = isoparse(compare_val)
            except ValueError:
                # Can not meet partition params as it not a date
                logger.warning(
                    f'{file_path} is not a valid date.',
                    extra={
                        'file_path': file_path,
                        'filterable': filterable
                    },
                    exc_info=True
                )

                return False

            filter_value = filter_value_date

        match = _eval_logical(
            op,
            field=compare_val,
            val=filter_value
        )

        if not match:
            # Short circuit as soon as we fail to match a filter.
            logger.debug(
                f"Excluding file with path '{file_path}' because it "
                f"contains the partitions '{found_partitions}' and the "
                f"user is filtering with '{field}{op}{filter_value}' "
                f"which for this path is {compare_val}'."
            )
            return False

    not_filtered = [
        x for x in query_partitions
        if not x['partition'] in found_partitions
    ]

    if not_filtered:
        logger.warning(
            f"These query partitions '{not_filtered}' were not found as "
            f"keys in the S3 path '{file_path}', so we are going to "
            'let this file through the filter but either the user has '
            'supplied an partition that does not exist or one of the S3 '
            'paths does not follow the partition pattern of the first S3 '
            'path in this instance.'
        )

    return True


def match_partitions(
    file_path: str,
    partitions: List[str],
):
    """
    Return True if the path contains the partition(s) provided.

    :param file_path:
    :param partitions:
    :return:
    """
    # Convert from a list of string to a dictionary of partition, operator &
    # value
    query_partitions = [
        potential.as_dict() for potential in
        [
            PartitionOperatorValueModel(x)
            for x in partitions
        ] if potential.valid
    ]

    return meets_partition_params(file_path, query_partitions)