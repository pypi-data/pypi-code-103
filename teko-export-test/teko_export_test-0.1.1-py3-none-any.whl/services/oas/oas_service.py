import json, pyaml, yaml
import sys
import urllib

from teko.helpers.clog import CLog
from teko.services.oas.parse.openapi3 import OpenAPI
from teko.services.oas.parse.openapi3.object_base import Map

class OasService:
    """
    Oas API docs:
    """
    def parse_file(self, file):
        spec = self.load_data(file)

        o = OpenAPI(spec, validate=True)
        # print(o.__slots__)
        self.print_class_object(o)
        # paths = parse_path(o)

        errors = o.errors()

        if errors:
            # print errors
            for e in errors:
                print('{}: {}'.format('.'.join(e.path), e.message[:300]))
            print()
            print('{} errors'.format(len(errors)))
            sys.exit(1)  # exit with error status
        else:
            print('OK')

    def diff_oas(self, code_spec, doc_spec):
        code_spec = self.load_data(code_spec)
        doc_spec = self.load_data(doc_spec)

        code_o = OpenAPI(code_spec, validate=True)
        doc_o = OpenAPI(doc_spec, validate=True)

        self.compare_api(code_o, doc_o, "spec")
        self.compare_api(doc_o, code_o, "real")
        # print(f'Result:\n{json.dumps(diff)}')
        print()
        CLog.info("Show comparison!")
        self.print_result(self.diff)

        # TODO parse error 2 spec

    diff = {"difference": {}, "miss": {}, "redundancy": {}}
    be_not_compared_schemas = []
    DIFFERENCE_STATUS = 'difference'
    MISS_STATUS = 'miss'
    REDUNDANCY_STATUS = 'redundancy'

    def print_result(self, result, count=0):
        for key, value in result.items():
            if "severity" in value.keys():
                if value["validation_status"] == self.MISS_STATUS:
                    print('--' * count, key, end="\n")
                elif value["validation_status"] == self.REDUNDANCY_STATUS:
                    print('++' * count, key, end="\n")
                elif value["validation_status"] == self.DIFFERENCE_STATUS:
                    print('  ' * count, key, end="\n")
                    print('--' * (count + 1), value["spec"], end="\n")
                    print('++' * (count + 1), value["real"], end="\n")
            else:
                print('  ' * count, key, end="\n")
                count += 1
                self.print_result(value, count)
                count -= 1

    def compare_api(self, code_spec, doc_spec, root="spec"):
        # compare paths object
        for key, doc_value in doc_spec.paths.items():
            if key not in code_spec.paths.keys():
                if (root == "spec"):
                    self.add_miss_or_redundancy_object(doc_spec.paths.path, key, 'miss')
                # root == "real"
                else:
                    self.add_miss_or_redundancy_object(doc_spec.paths.path, key, 'redundancy')
            else:
                for k, v in code_spec.paths.items():
                    if k == key:
                        code_value = v
                        self.compare_object(code_value, doc_value, root=root)

        # compare similar components (class model) of doc and code
        #   todo: before check parse error if miss model => key always exist in code_spec.components
        for key, doc_value in doc_spec.components.schemas.items():
            for k, v in code_spec.components.schemas.items():
                if k == key:
                    code_value = v
                    self.compare_object(code_value, doc_value, root=root)

    def compare_object(self, code_spec, doc_spec, root="spec", name_parameter=""):
        for item in doc_spec.__slots__:
            if item == 'dct' or item == 'example':
                continue

            if "parameters" not in doc_spec.path:
                name_parameter = ""

            if isinstance(getattr(doc_spec, item), Map):
                if not hasattr(code_spec, item) or (not isinstance(getattr(code_spec, item), Map)):
                    if (root == "spec"):
                        self.add_diff_object(doc_spec.path, item, 'miss', getattr(doc_spec, item))
                    # root == "real"
                    else:
                        self.add_diff_object(doc_spec.path, item, 'redundancy', getattr(doc_spec, item))
                    continue

                for key, doc_value in getattr(doc_spec, item).items():
                    if key not in getattr(code_spec, item).keys():
                        if (root == "spec"):
                            self.add_diff_object(getattr(doc_spec, item).path, key, 'miss', doc_value)
                        # root == "real"
                        else:
                            self.add_diff_object(getattr(doc_spec, item).path, key, 'redundancy', doc_value)
                        continue
                    else:
                        for k, v in getattr(code_spec, item).items():
                            if k == key:
                                code_value = v
                                self.compare_object(code_value, doc_value, root)

            elif isinstance(getattr(doc_spec, item), list) and getattr(doc_spec, item):
                if not hasattr(code_spec, item) or not isinstance(getattr(code_spec, item), list):
                    if (root == "spec"):
                        self.add_diff_object(doc_spec.path, item, 'miss', getattr(doc_spec, item))
                    # root == "real"
                    else:
                        self.add_diff_object(doc_spec.path, item, 'redundancy', getattr(doc_spec, item))
                else:
                    # if parameter object then compare name to check miss param
                    if item == 'parameters':
                        name_parameters_code = set(x.name for x in getattr(code_spec, item))
                        miss_parameter_objects = [x for x in getattr(doc_spec, item) if
                                                  x.name not in name_parameters_code]
                        # check code miss parameters
                        if miss_parameter_objects:
                            for obj in miss_parameter_objects:
                                if (root == "spec"):
                                    self.add_diff_object(obj.path, obj.name, 'miss', obj, '', obj.name)
                                # root == "real"
                                else:
                                    self.add_diff_object(obj.path, obj.name, 'redundancy', obj, '', obj.name)

                    # compare object
                    for o_doc in getattr(doc_spec, item):
                        # i: instance (Parameter)
                        if hasattr(o_doc, '__slots__'):
                            # find code_obj and doc_obj having same name
                            for o_code in getattr(code_spec, item):
                                if o_code.name == o_doc.name:
                                    self.compare_object(o_code, o_doc, root, o_doc.name)
                                    break

                        # i: string
                        elif isinstance(o_doc, str):
                            if o_doc not in getattr(code_spec, item):
                                if (root == "spec"):
                                    self.add_diff_object(doc_spec.path, item, 'miss', o_doc)
                                else:
                                    self.add_diff_object(doc_spec.path, item, 'redundancy', o_doc)

            elif getattr(doc_spec, item) or isinstance(getattr(doc_spec, item), bool):
                if item.startswith('_'):
                    continue

                # check item in code_spec
                if not hasattr(code_spec, item):
                    if (root == "spec"):
                        self.add_diff_object(doc_spec.path, item, 'miss', getattr(doc_spec, item))
                    # root == "real"
                    else:
                        self.add_diff_object(doc_spec.path, item, 'redundancy', getattr(doc_spec, item))

                # item: class object
                elif hasattr(getattr(doc_spec, item), '__slots__'):
                    if root == 'spec' and getattr(doc_spec, item).path[0] == "components" and \
                            getattr(doc_spec, item).path[1] == "schemas":
                        if getattr(doc_spec, item).path[-1] != getattr(code_spec, item).path[-1]:
                            self.add_diff_object(doc_spec.path, item, self.DIFFERENCE_STATUS, getattr(doc_spec, item).path[-1],
                                            getattr(code_spec, item).path[-1])
                    else:
                        self.compare_object(getattr(code_spec, item), getattr(doc_spec, item), root, name_parameter)

                # item: string / bool
                elif getattr(doc_spec, item) != getattr(code_spec, item):
                    # item is not method: 'get', etc...
                    # todo check item exist
                    # if item != sub_paths:
                    if root == 'spec':
                        self.add_diff_object(doc_spec.path, item, self.DIFFERENCE_STATUS, getattr(doc_spec, item),
                                        getattr(code_spec, item), name_parameter)
                # item: string, equal and include model class
                elif item == 'ref' and root == 'spec':
                    # doc_spec.path, item, getattr(doc_spec, item)
                    name_schema = getattr(doc_spec, item).split('/')[-1]
                    if name_schema not in self.be_not_compared_schemas:
                        self.be_not_compared_schemas.append(name_schema)

    def add_diff_object(self, paths, key, validation_status, doc_value, code_value='', name_different_parameter=""):
        if not isinstance(doc_value, str) and not isinstance(doc_value, list) and not isinstance(doc_value,bool) and \
                not isinstance(doc_value, int) and not isinstance(doc_value, float):
            doc_value = 'CLASS OBJECT (DETAIL?)'
        if key == 'in_':
            key = 'in'
        # if object is element of Parameter object
        if name_different_parameter != "":
            index_parameters = paths.index("parameters")
            # if miss/ redundancy, name = key and paths[-1] is string of integer
            if index_parameters == len(paths) - 2 and name_different_parameter == key:
                paths = paths[:-1]
            # difference then paths[-1] which is string of integer, is set by name_param
            else:
                paths[index_parameters + 1] = name_different_parameter

        if validation_status == self.DIFFERENCE_STATUS:
            if key in ["summary", "description", "operationId"]:
                value_status = {
                    'spec': doc_value,
                    'real': code_value,
                    'severity': 'warning',
                    'validation_status': validation_status
                }
            else:
                value_status = {
                    'spec': doc_value,
                    'real': code_value,
                    'severity': 'error',
                    'validation_status': validation_status
                }
        # miss or redundancy
        else:
            if validation_status == self.MISS_STATUS:
                spec = doc_value
                real = None
            elif validation_status == self.REDUNDANCY_STATUS:
                spec = None
                real = doc_value
            if key in ["summary", "description", "operationId"]:
                value_status = {
                    'spec': spec,
                    'real': real,
                    'severity': 'warning',
                    'validation_status': validation_status
                }
            else:
                value_status = {
                    'spec': spec,
                    'real': real,
                    'severity': 'error',
                    'validation_status': validation_status
                }

        # change elements(api_path, method) of paths to one element "api method"
        if paths[2] in ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']:
            paths[1] = paths[1] + " " + paths[2].upper()
            paths.pop(2)

        prev_diff = self.diff["difference"]
        for index in range(0, len(paths)):
            if paths[index] not in prev_diff.keys():
                remain_paths = paths[index + 1:]
                beside_value = {key: value_status}

                value_diff = {}
                for sub_path in remain_paths[::-1]:
                    value_diff = {sub_path: beside_value}
                    beside_value = value_diff
                prev_diff[paths[index]] = value_diff
                prev_diff = prev_diff[paths[index]]
                break
            prev_diff = prev_diff[paths[index]]
        if (index == len(paths) - 1) and (key not in prev_diff.keys()):
            prev_diff[key] = value_status

    def add_miss_or_redundancy_object(self, paths, key, status):
        # change elements(api_path, method) of paths to one element "api method"
        if len(paths) >= 2 and paths[2] in ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']:
            paths[1] = paths[1] + " " + paths[2].upper()
            paths.pop(2)

        value = {
            'validation_status': status,
            'description': 'No more detail!',
            "severity": "error"
        }

        prev_diff = self.diff[status]
        for index in range(0, len(paths)):
            if paths[index] not in prev_diff.keys():
                remain_paths = paths[index + 1:]
                beside_value = {key: value}
                value_diff = {}
                for sub_path in remain_paths[::-1]:
                    value_diff = {sub_path: beside_value}
                    beside_value = value_diff
                prev_diff[paths[index]] = value_diff
                prev_diff = prev_diff[paths[index]]
                break
            prev_diff = prev_diff[paths[index]]
        if (index == len(paths) - 1) and (key not in prev_diff.keys()):
            prev_diff[key] = value

    def print_class_object(self, o, count=1):
        for item in o.__slots__:
            if item == 'dct':
                return
            if isinstance(getattr(o, item), Map):
                # print('  ' * count, '-------------------------')
                print('  ' * count, item, end=" ")
                print(type(getattr(o, item)), end=" ")
                # print(getattr(o, item))
                print()
                for key, value in getattr(o, item).items():
                    print('  ' * (count + 1), key)
                    self.print_class_object(value, count + 2)
            elif isinstance(getattr(o, item), list) and getattr(o, item):
                print('  ' * count, item, end=" ")
                print(type(getattr(o, item)), end=" ")
                # print(getattr(o, item))
                print()
                for value in getattr(o, item):
                    if isinstance(value, str):
                        print('  ' * (count + 1), value)
                    else:
                        self.print_class_object(value, count + 1)
            elif getattr(o, item):
                if item.startswith('_'):
                    return
                print('  ' * count, item if item != 'in_' else 'in', end=" ")
                print(type(getattr(o, item)), end=" ")
                if hasattr(getattr(o, item), '__slots__'):
                    # print('  ' * count, getattr(o, item).__slots__)
                    print()
                    self.print_class_object(getattr(o, item), count + 1)
                else:
                    print(getattr(o, item))
            elif isinstance(getattr(o, item), bool):
                if item.startswith('_'):
                    return
                print('  ' * count, item, end=" ")
                print(getattr(o, item))

    def load_data(self, spec_parameter: str):
        # TODO: http with yaml, error parse json to yaml spec to object spec
        if 'http' in spec_parameter:
            CLog.info('url')
            with urllib.request.urlopen(spec_parameter) as response:
                loaded_json = json.loads(response.read())
                spec = yaml.dump(loaded_json)
                return loaded_json
        elif '.yaml' in spec_parameter:
            try:
                with open(spec_parameter) as f:
                    spec = yaml.safe_load(f.read())
                    return spec
            except OSError:
                CLog.info(f"Could not open/read file: {spec_parameter}")
                exit()
        elif '.json' in spec_parameter:
            CLog.info('Json')
            try:
                with open(spec_parameter, 'r') as f:
                    spec = json.loads(f.read())
                    return spec
            except OSError:
                CLog.info(f"Could not open/read file: {spec_parameter}")
                exit()
        else:
            CLog.info('Failed to load data. Parameters is url, or path to *.json or *.yaml!')
            exit()


if __name__ == "__main__":
    oas_srv = OasService()




