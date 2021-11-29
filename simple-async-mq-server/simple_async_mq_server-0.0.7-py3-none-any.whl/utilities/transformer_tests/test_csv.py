from io import StringIO
from models.message_queue import MessageQueue
from models.subscriber import Subscriber
from utilities import transformer as t

### CSV
csv_obj = 'a,b,c\n1,2,3'
csv_array = 'a,b,c\n1,2,3\n3,4,5'


csv_dict = t.csv_to_dict(csv_array)
print("csv_dict")
print(csv_dict)

# # CSV TO XML
# xml = t.dict_to_xml(csv_dict)
# print("xml")
# print(xml)

# CSV TO JSON
json = t.dict_to_json(csv_dict)
print("json")
print(json)