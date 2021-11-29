from io import StringIO
from models.message_queue import MessageQueue
from models.subscriber import Subscriber
from utilities import transformer as t

### XML
# Xml —> dict —> json / csv / tsv
xml_object = """<?xml version="1.0" ?>
<person>
  <name>john</name>
  <age>20</age>
</person>
"""
xml_list= """<?xml version="1.0" ?>
<students>
 <student>
   <name>Rick Grimes</name>
   <age>35</age>
   <subject>Maths</subject>
   <gender>Male</gender>
 </student>
 <student>
   <name>Daryl Dixon </name>
   <age>33</age>
   <subject>Science</subject>
   <gender>Male</gender>
 </student>
</students>
"""

xml_dict = t.xml_to_dict(xml_object)
print("xml_dict")
print(xml_dict)

# XML to JSON
# json = t.dict_to_json(xml_dict)
# print("json")
# print(json)

# XML to CSV
csv = t.dict_to_csv(xml_dict)
print("csv")
print(csv)




