import json


class API:

    def __init__(self, performance=False):
        self.performance = performance
        self.__result = None
        self.__syntax = None

    @property
    def get_start_class(self):
        if self.performance:
            return f'''from locust import HttpUser, task
        
            
class WebsiteUser(HttpUser):
        
        '''
        else:
            return '''
import allure
import api
'''

    @property
    def get_headers_example(self):
        return str({'Content-Type': 'application/json', 'Accept': 'application/json'})

    @property
    def get_params_example(self):
        return {'parameter1': True, 'parameter2': 2, 'parameter3': 'example'}

    @property
    def get_body_example(self):
        return {
            "jsonObject": {
                "type1": "MultiPolygon1",
                "typ2": "MultiPolygon2",
            }
        }

    @property
    def expected_status_code_method(self):
        return """
        
@allure.step("Expected Status Code")
def analyze_response(res, expected_status_code):
    if res.status_code != expected_status_code:
        assert False
    else:
        print(f"status code is {res.status_code}")"""

    def set_method(self, method, resource, params=None, headers=None, body=None, name='service_1', domain=None,
                   expected_status_code=200):
        # domain and resource validation
        if domain[len(domain) - 1] == '/':
            domain[len(domain) - 1] = ''
            domain = f"/{domain}"

        if resource[0] != '/':
            resource = f"/{resource}"

        if self.performance:
            self.__syntax = f"self.client.{method}(url='{resource}'"
        else:
            self.__syntax = f"""   
@allure.feature("Set Feature For {name}")
@allure.description("Set Description For {name}")        
def test_{name}():
    component_{name}()

@allure.step("Set Step Description For {name}")
def component_{name}():
     api_instance = api.rest_api.ApiCapabilities()
     response = api_instance.{method}_request(url='{domain}{resource}?'"""
        if params is not None and len(params) > 0:
            self.__syntax += f", params={params.replace('true', 'True').replace('false', 'False')}"

        if headers is not None and len(headers) > 0:
            self.__syntax += f", headers={headers}"

        if body is not None and len(body) > 0:
            self.__syntax += f", data={body}"

        if self.performance:
            self.__result = f'''
        @task
        def {name}(self):
            {self.__syntax})
'''

        else:
            self.__result = f'''
{self.__syntax})
     analyze_response(response, {expected_status_code})
'''
        return f"{self.__result}"


class AzureTC:

    def __init__(self, file_path, assigned_name):
        self.__steps = None
        self.__step_object = None
        self.__tc_object = ReadResults(file_path)
        self.__assigned_name = assigned_name

    def set_step(self, step_id):
        return f"<step id=\"{step_id}\" type=\"ValidateStep\">" \
               "<parameterizedString\n" \
               f"isformatted=\"true\">{self.__step_object}" \
               "</parameterizedString>" \
               "<parameterizedString\n" \
               f"isformatted=\"true\">{self.__step_object}" \
               "</parameterizedString>\n" \
               "<description/>" \
               "</step>"

    def __get_steps_object(self):
        result = f"<steps id=\"0\" last=\"{len(self.__steps)}\">"
        for step_index, self.__step_object in enumerate(self.__steps):
            result += self.set_step(step_id=step_index)

        return f"{result}\n</steps>"

    def build_json_body(self):
        """
        Body template for the azures post request
        Contain: Test case title , assigned name (owner) and steps
        return: json body with title ,AssignedTo and Steps params
        """
        self.__steps = self.__tc_object.export_steps()
        body_of_step = [
            {
                "op": "add",
                "path": "/fields/System.Title",
                "value": f"{self.__tc_object.get_name}"
            },
            {
                "op": "add",
                "path": "/fields/System.AssignedTo",
                "value": f"{self.__assigned_name}"
            },
            {
                "op": "add",
                "path": "/fields/Microsoft.VSTS.TCM.Steps",
                "value": f"{self.__get_steps_object()}"
            }
        ]
        return body_of_step


class ReadResults:
    """
    ReadResults
    This class extract json values by field name
    """

    def __init__(self, json_path):
        self.__path = json_path
        self._json = self.read_json_object()

    @property
    def get_name(self):
        return self._json.get('name')

    @property
    def get_test_case_id(self):
        return self._json.get('testCaseId')

    @property
    def get_status(self):
        return self._json.get('status')

    @property
    def get_labels(self):
        return self._json.get('labels')

    @property
    def get_steps(self):
        return self._json.get('steps')

    @property
    def get_parameters(self):
        return self._json.get('parameters')

    @property
    def get_attachments(self):
        return self._json.get('attachments')

    @property
    def get_start_time(self):
        return self._json.get('start')

    @property
    def get_end_time(self):
        return self._json.get('stop')

    @property
    def get_test_case_history_id(self):
        return self._json.get('historyId')

    @property
    def get_test_case_uuid(self):
        return self._json.get('uuid')

    def read_json_object(self):
        file = open(self.__path, 'r')
        json_object = json.load(file)
        file.close()
        return json_object

    def export_steps(self):
        index = 0
        steps = []
        steps_object = self.get_steps

        for step in steps_object:
            steps.insert(index, step.get('name'))
            index += 1
            while 'steps' in step:
                step = step.get('steps')
                for temp_step in step:
                    steps.insert(index, temp_step.get('name'))
                    index += 1
                if 'steps' in temp_step:
                    step = temp_step

        return steps
