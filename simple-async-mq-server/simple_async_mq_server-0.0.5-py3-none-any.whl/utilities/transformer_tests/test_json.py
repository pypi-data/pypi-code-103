from io import StringIO
from models.message_queue import MessageQueue
from models.subscriber import Subscriber
from utilities import transformer as t
import xmltodict, json, dict2xml, pandas as pd

### JSON 
# Json —> dict —> xml / csv / tsv

json_obj = '{"person": {"name": "john", "age": "20"}}'
json_array = '[{"name": "john", "age": "20"},{"name": "john", "age": "20"}]'

json_dict = t.json_to_dict(json_array)
# JSON to CSV
csv = t.dict_to_csv(json_dict)
print("csv")
print(csv)

# JSON TO XML
xml = t.dict_to_xml(json_dict)
print("xml")
print(xml)


