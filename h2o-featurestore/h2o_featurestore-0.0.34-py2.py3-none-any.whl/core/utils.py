import google.protobuf.text_format
from google.protobuf.timestamp_pb2 import Timestamp


class Utils:
    @staticmethod
    def pretty_print_proto(m):
        def printer(msg, indent, as_one_line):
            if msg.DESCRIPTOR == Timestamp.DESCRIPTOR:
                return str(msg.ToDatetime().isoformat())
            return None

        return google.protobuf.text_format.MessageToString(m, message_formatter=printer)

    @staticmethod
    def timestamp_to_string(timestamp):
        if timestamp.ByteSize() != 0:
            return timestamp.ToDatetime().isoformat()
        else:
            return None


def get_index_of_matching_ending_angular_bracket(string):
    stack = []
    for idx, ch in enumerate(string):
        if ch == "<":
            stack.append(idx)
        elif ch == ">":
            if len(stack) == 1:
                return idx
            else:
                stack.pop()


def extract_pair(schema):
    from .schema import Column

    splits = schema.split()
    col_name = splits[0]
    remaining_schema = " ".join(splits[1:])
    if remaining_schema.upper().startswith(
        "STRUCT"
    ) or remaining_schema.upper().startswith("ARRAY"):
        idx = get_index_of_matching_ending_angular_bracket(remaining_schema)
        data_type = remaining_schema[: idx + 1].strip()
        remaining_schema = remaining_schema[idx + 1 :].strip()
        remaining_schema = remaining_schema[1:].strip()
    else:
        data_type = remaining_schema.lstrip().split(",")[0].strip()
        remaining_schema = ",".join(remaining_schema.split(",")[1:]).strip()
    return Column(col_name, data_type), remaining_schema


def extract_columns(schema):
    if schema:
        col, remaining = extract_pair(schema)
        return [col] + extract_columns(remaining)
    else:
        return []
