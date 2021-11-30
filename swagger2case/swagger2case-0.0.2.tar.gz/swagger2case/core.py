import io
import json
import logging
import os
import yaml
import re
from urllib.parse import urlsplit

from swagger2case.compat import ensure_ascii
from swagger2case.parser import parse_value_from_type


class SwaggerParser(object):
    def __init__(self, swagger_testcase_file):
        self.swagger_testcase_file = swagger_testcase_file

    def read_swagger_data(self):
        with open(self.swagger_testcase_file, encoding='utf-8', mode='r') as file:
            swagger_data = json.load(file)

        return swagger_data
    
    def parse_url(self, base_path, request_url):
        url = ""
        if isinstance(request_url, str):
            url = request_url
        elif isinstance(request_url, dict):
            if "raw" in request_url.keys():
                url= request_url["raw"]
        return '{}{}'.format('' if base_path == '/' else base_path, url)
    
    def parse_request_data(self, type, request_data, api):
        data = {}
        for d in request_data:
            if d.get('in') != type: continue
            if d.get('schema'):
                data = self.parse_object(d.get('schema').get('properties'), api)
            else:
                key = d["name"]
                value = d.get('default') or d["type"]
                for v in re.findall(r'\{\{.+?\}\}', key):
                    api['config']["variables"][v[2:-2]] = ''
                    key = key.replace(v, '${}'.format(v[2:-2]))
                for v in re.findall(r'\{\{.+?\}\}', value):
                    api['config']["variables"][v[2:-2]] = ''
                    value = value.replace(v, '${}'.format(v[2:-2]))
                data[key] = value
        return data

    def parse_object(self, object_data, api):
        data = {}
        for k, d in object_data and object_data.items() or {}:
            if d.get('type') == 'object': 
                temp = self.parse_object(d.get('properties'), api)
                data[k] = temp
            else:
                key = k
                value = d.get('type')
                for v in re.findall(r'\{\{.+?\}\}', key):
                    api['config']["variables"][v[2:-2]] = ''
                    key = key.replace(v, '${}'.format(v[2:-2]))
                for v in re.findall(r'\{\{.+?\}\}', value):
                    api['config']["variables"][v[2:-2]] = ''
                    value = value.replace(v, '${}'.format(v[2:-2]))
                data[key] = value
        return data

    def parse_each_item(self, item, url='/'):
        """ parse each item in swagger to testcase in httprunner
        """
        api = dict(config=dict(base_url='$base_url'), teststeps=[])
        api['config']["name"] = item["summary"]
        api['config']["variables"] = dict()

        request = {}
        request["method"] = item["method"].upper()

        request["url"] = url

        if request["method"].upper() == "GET":
            request["headers"] = self.parse_request_data('header', item["parameters"], api)
            request["params"] = self.parse_request_data('query', item["parameters"], api)
        else:
            for v in re.findall(r'\{\{.+?\}\}', url):
                api['config']["variables"][v[2:-2]] = ''
                url = url.replace(v, '${}'.format(v[2:-2]))
            request["headers"] = self.parse_request_data('header', item["parameters"], api)

            body = self.parse_request_data('body', item["parameters"], api) 
            form_data = self.parse_request_data('formData', item["parameters"], api)

            body = dict(body, **form_data)

            if not request["headers"].get('Content-Type'):
                if (not form_data) and isinstance(body, (dict, list)):
                    request["json"] = body
                else:
                    request["data"] = body
            elif request["headers"].get('Content-Type', '').find('json') < 0 or form_data:
                request["data"] = body
            else:
                request["json"] = body

        api["teststeps"].append(dict(name=url, request=request, validate=[dict(eq=['status_code', 200])]))
        return api
    
    def parse_items(self, items, folder_name=None, base_path='/'):
        result = []
        for item_key, item_value in items.items():
            if "parameters" not in item_value.keys():
                temp = self.parse_items(item_value, folder_name, self.parse_url(base_path, item_key))
                result += temp
            else:
                folder = item_value.get("summary", '').replace(" ", "_")
                if folder_name:
                    folder = os.path.join(folder_name, folder)
                item_value['method'] = item_key
                api = self.parse_each_item(item_value, base_path)
                api["folder_name"] = folder
                result.append(api)
        return result

    def parse_data(self):
        """ dump swagger data to json testset
        """
        logging.info("Start to generate yaml testset.")
        swagger_data = self.read_swagger_data()

        result = self.parse_items(swagger_data["paths"], swagger_data.get('info', {}).get('title'), swagger_data.get('basePath', '/'))
        return result, swagger_data.get('info', {}).get('title')

    def save(self, data, output_dir, output_file_type="yml", name=''):
        count = 0
        output_dir = os.path.join(output_dir, "TestCases", "APICase")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        test_suites = dict(config=dict(name=name, variables=dict(base_url='')), testcases=[])
        for each_api in data:
            count += 1
            file_name = "{}.{}".format(count, output_file_type)
            
            folder_name = each_api.pop("folder_name")
            if folder_name:
                folder_path = os.path.join(output_dir, folder_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                file_path = os.path.join(folder_path, file_name)
            else:
                file_path = os.path.join(output_dir, file_name)
            if os.path.isfile(file_path):
                logging.error("{} file had exist.".format(file_path))
                continue
            if output_file_type == "json":
                with io.open(file_path, 'w', encoding="utf-8") as outfile:
                    my_json_str = json.dumps(each_api, ensure_ascii=ensure_ascii, indent=4)
                    if isinstance(my_json_str, bytes):
                        my_json_str = my_json_str.decode("utf-8")

                    outfile.write(my_json_str)
            else:
                with io.open(file_path, 'w', encoding="utf-8") as outfile:
                    my_json_str = json.dumps(each_api, ensure_ascii=ensure_ascii, indent=4)
                    yaml.dump(each_api, outfile, allow_unicode=True, default_flow_style=False, indent=4)
            test_suites['testcases'].append(dict(name=each_api.get('config').get('name'), testcase=file_path.replace('\\', '/')))    
            logging.info("Generate JSON testset successfully: {}".format(file_path))
        if test_suites.get('testcases'):
            folder_path = os.path.join(output_dir)
            file_name = "TEST_{}_testSuite.{}".format(test_suites.get('config').get('name'), output_file_type)
            file_path = os.path.join(folder_path, file_name)
            if output_file_type == "json":
                with io.open(file_path, 'w', encoding="utf-8") as outfile:
                    my_json_str = json.dumps(test_suites, ensure_ascii=ensure_ascii, indent=4)
                    if isinstance(my_json_str, bytes):
                        my_json_str = my_json_str.decode("utf-8")

                    outfile.write(my_json_str)
            else:
                with io.open(file_path, 'w', encoding="utf-8") as outfile:
                    my_json_str = json.dumps(test_suites, ensure_ascii=ensure_ascii, indent=4)
                    yaml.dump(test_suites, outfile, allow_unicode=True, default_flow_style=False, indent=4)
            logging.info("Generate testsuite successfully: {}".format(file_path))
