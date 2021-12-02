import logging
import os
import inspect
from vtb_py_logging import get_data_record

try:
    import sqlparse
    _sql_parser = True
except ImportError:
    _sql_parser = False


class SyslogFilter(logging.Filter):
    hostname = os.getenv('HOSTNAME')

    def filter(self, record):
        record.hostname = SyslogFilter.hostname
        return True


class SQLExtraFilter(logging.Filter):
    def __init__(self,  name=''):
        super().__init__(name)

    @staticmethod
    def call_stack():
        stack = []
        start = False
        frames = inspect.stack()
        first_func = frames[0].function
        for frame in frames:
            func_name = frame.function
            if not start:
                if func_name == 'execute_sql':
                    start = True
            elif func_name == 'view':
                break
            elif func_name not in (first_func, "<module>"):
                stack.append(func_name)
        return '.'.join(reversed(stack))

    def filter(self, record: logging.LogRecord) -> bool:
        res = super().filter(record)
        if not res:
            return False

        sql = record.__dict__.get("sql")
        if not sql:
            return True

        if _sql_parser:
            sql = sqlparse.format(sql, reindent=True, keyword_case='upper')

        record.sql_call_stack = self.call_stack()

        msg = f"{record.duration:.3f} {sql};\nparams={record.params}\n{record.sql_call_stack}"
        record.msg = msg
        record.args = []
        return True


class OrderExtraFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        res = super().filter(record)
        if not res:
            return False

        order_id, action_id, graph_id, node, action_type, orchestrator_id = get_data_record(record)
        if order_id is not None or action_id is not None or graph_id is not None or action_type is not None:
            record.msg += f"\n" \
                          f'order_id: {order_id}\n' \
                          f'action_id: {action_id}\n' \
                          f'graph_id: {graph_id}\n' \
                          f'node: {node}\n' \
                          f'action_type: {action_type}\n' \
                          f'orchestrator_id: {orchestrator_id}'
        return True
