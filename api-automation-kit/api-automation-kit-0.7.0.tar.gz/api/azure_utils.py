import json
import allure
import xmltojson
from azure.devops.v5_1.test_plan import TestPlanClient
from msrest.authentication import BasicAuthentication
import base64
import os
import api


class AzureTestPlan:

    def __init__(self):
        self.__test_plan = None
        self.__test_suite = None
        self.__test_cases = None
        self.__test_case = None
        self.__xml_steps = None

    @property
    def get_access_token(self):
        """
        Get access token from environment variables configuration
        """
        return os.environ.get('access-token')

    @property
    def get_organization_url(self):
        """
        Get organization url from environment variables configuration
        """
        return os.environ.get('organization-url')

    @property
    def get_project(self):
        """
        Get organization url from environment variables configuration
        """
        return os.environ.get('project')

    @property
    def get_owner(self):
        """
        Get azure owner from environment variables configuration
        """
        return os.environ.get('owner')

    @property
    def get_authorization(self):
        return str(base64.b64encode(bytes(':' + self.get_access_token, 'ascii')), 'ascii')

    @property
    def get_headers_object(self):
        """
        header template for the azure request
        """
        return {
            'Content-Type': 'application/json-patch+json',
            'Authorization': 'Basic ' + self.get_authorization
        }

    @property
    def get_credentials(self):
        """
        This function used to get tests plans connection by the access token.
        """
        return BasicAuthentication('', self.get_access_token)

    @property
    def get_tc_url(self):
        """
        The function return test case url by using the organization url and project name for the path template.
        """
        return f"{self.get_organization_url}/{self.get_project}/_apis/wit/workitems/$Test%20Case?api-version=5.1"

    @allure.step("get test plan object")
    def get_test_plan(self):
        """
        This function return TestPlanClient object.
        """
        return TestPlanClient(self.get_organization_url, self.get_credentials)

    @allure.step("get test case")
    def get_test_case(self, plan_id: int, suite_id: int, test_case_id: int, get_all_tests=False):
        self.__test_plan = self.get_test_plan()
        self.__test_cases = self.__test_plan.get_test_case(project=self.get_project, plan_id=plan_id,
                                                           suite_id=suite_id,
                                                           test_case_ids=str(test_case_id))
        results = []
        if get_all_tests:
            for index, self.__test_case in enumerate(self.__test_cases):
                results.insert(index, self.__extract_test_case_data())

        else:
            for index, self.__test_case in enumerate(self.__test_cases):
                if self.__test_case.work_item.id == test_case_id:
                    return self.__extract_test_case_data()

        return results

    @allure.step("extract test case data")
    def __extract_test_case_data(self):
        tc_details = {'id': self.__test_case.work_item.id, 'name': self.__test_case.work_item.name}
        work_item = self.__test_case.work_item.work_item_fields
        self.__xml_steps = work_item[0].get('Microsoft.VSTS.TCM.Steps')
        steps = self.__convert_xml_to_json(self.__xml_steps)
        steps = {'Microsoft.VSTS.TCM.Steps': steps}
        work_item[0] = steps
        work_item.insert(len(work_item), tc_details)
        return work_item

    @allure.step("convert xml to json")
    def __convert_xml_to_json(self, xml, save_location_path=None):
        """
        The function gets a xml file and saves location path and convert it to json file into the received path
        """
        json_content = xmltojson.parse(xml).replace('None', 'null')
        if save_location_path is not None:
            json_file = open(save_location_path, "w")
            json_file.write(json_content)
            json_file.close()
        else:
            return json.loads(json_content)

    @allure.step("create new test case on azure")
    def create_new_tc_on_azure(self, json_path):
        """
        Write a new test case on the azures board
        """
        azure_tc = api.generator.AzureTC(file_path=json_path, assigned_name=self.get_owner)
        api_instance = api.rest_api.ApiCapabilities()
        response = api_instance.post_request(url=self.get_tc_url, body=json.dumps(azure_tc.build_json_body()),
                                             headers=self.get_headers_object)
        return response
