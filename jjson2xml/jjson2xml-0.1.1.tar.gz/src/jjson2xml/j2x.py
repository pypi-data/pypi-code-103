import numbers
import xml.etree.ElementTree as ET
       
def convert_dict(obj,parent=None):
    element=ET.Element('root')
    for key, val in obj.items():
        if '@' not in key :
            if parent==None:
                element = ET.Element(key)
            else:
                element = ET.SubElement(parent, key) 
            if isinstance(val, dict):
                hashtag_vals = dict(filter(lambda x:'#text' in x[0], val.items()))
                attr = dict(filter(lambda x:'@' in x[0], val.items()))
                for attr_key, attr_val in attr.items():
                    element.set(attr_key.replace('@',''),attr_val)
                if hashtag_vals:
                    val = hashtag_vals['#text']

            if isinstance(val, numbers.Number) or isinstance(val, str):
                element.text=val
            elif isinstance(val, dict):
                convert_dict(val,parent=element)
    
    return ET.canonicalize(ET.tostring(element,encoding='utf-8').decode('utf8'),strip_text=True)
          
def json2xml(obj):
    if isinstance(obj, dict):
        return convert_dict(obj)
