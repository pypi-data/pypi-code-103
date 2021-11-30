from __future__ import print_function
from .logexception import LogException
import six
import logging

from .putlogsrequest import PutLogsRequest



MAX_INIT_SHARD_COUNT = 200

logger = logging.getLogger(__name__)



def list_more(fn, offset, size, batch_size, *args):
    """list all data using the fn
    """
    if size < 0:
        expected_total_size = six.MAXSIZE
    else:
        expected_total_size = size
        batch_size = min(size, batch_size)

    response = None
    total_count_got = 0
    while True:
        ret = fn(*args, offset=offset, size=batch_size)
        if response is None:
            response = ret
        else:
            response.merge(ret)

        count = ret.get_count()
        total = ret.get_total()
        offset += count
        total_count_got += count
        batch_size = min(batch_size, expected_total_size - total_count_got)

        if count == 0 or offset >= total or total_count_got >= expected_total_size:
            break

    return response


def put_logs_auto_div(client, req, div=1):
    try:
        count = len(req.logitems)
        p1 = count // 2

        if div > 1 and p1 > 0:
            # divide req into multiple ones
            req1 = PutLogsRequest(project=req.project, logstore=req.logstore, topic=req.topic, source=req.source,
                                  logitems=req.logitems[:p1],
                                  hashKey=req.hashkey, compress=req.compress, logtags=req.logtags)
            req2 = PutLogsRequest(project=req.project, logstore=req.logstore, topic=req.topic, source=req.source,
                                  logitems=req.logitems[p1:],
                                  hashKey=req.hashkey, compress=req.compress, logtags=req.logtags)
            res = put_logs_auto_div(client, req1)
            return put_logs_auto_div(client, req2)
        else:
            return client.put_logs(req)
    except LogException as ex:
        if ex.get_error_code() == 'InvalidLogSize':
            return put_logs_auto_div(client, req, div=2)
        raise ex



