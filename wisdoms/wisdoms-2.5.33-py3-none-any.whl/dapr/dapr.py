import json
from dapr.clients import DaprClient
def dapr_invoke(app, method, data, http_verb="post", **kwargs):
    """
    dapr http invoke
    
    :param app: app_id
    :param method: 方法名称
    :http_verb: http请求方法
    :return:
    """
    with DaprClient() as d:
        res = d.invoke_method(app, method, json.dumps(data), http_verb=http_verb, **kwargs)
        return res