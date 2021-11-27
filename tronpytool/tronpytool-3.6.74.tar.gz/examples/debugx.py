import codecs
import json
#result = codecs.open("sk.json", 'r', 'utf-8-sig')
resul11 = """
{"result": true, "txid": "854c355e1464fab1b92e6ddd64a214d3bf7df31b38cb9931b19fbbfdd9a5d922", 
"transacetion": 
{"visible": false, "txID": "854c355e1464fab1b92e6ddd64a214d3bf7df31b38cb9931b19fbbfdd9a5d922", 
"contract_address": "41b04539876c41985563793a2b6cd118de9b8fadb4"}}

"""
print(resul11)
if "transaction" not in json.loads(resul11):
    print("not okay transaction")
else:
    print("yes")