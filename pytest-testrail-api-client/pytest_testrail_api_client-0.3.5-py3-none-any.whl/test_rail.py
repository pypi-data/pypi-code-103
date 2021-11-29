from pytest_testrail_api_client.api.cases_api import CasesApi
from pytest_testrail_api_client.api.congif_api import ConfigsApi
from pytest_testrail_api_client.api.milestones_api import MilestonesApi
from pytest_testrail_api_client.api.plans_api import PlansApi
from pytest_testrail_api_client.api.project_api import ProjectApi
from pytest_testrail_api_client.api.results_api import ResultsApi
from pytest_testrail_api_client.api.runs_api import RunsApi
from pytest_testrail_api_client.api.sections_api import SectionsApi
from pytest_testrail_api_client.api.service_api import ServiceApi
from pytest_testrail_api_client.api.small_api import TestsApi, StatusesApi, CaseTypesApi, TemplatesApi, CaseFieldsApi, \
    ResultsFieldsApi, PrioritiesApi, SharedStepsApi, ReportsApi
from pytest_testrail_api_client.api.suites_api import SuitesApi
from pytest_testrail_api_client.api.user_api import UsersApi
from pytest_testrail_api_client.modules.session import Session


class TestRail(Session):

    @property
    def projects(self):
        return ProjectApi(self)

    @property
    def tests(self):
        return TestsApi(self)

    @property
    def cases(self):
        return CasesApi(self)

    @property
    def statuses(self):
        return StatusesApi(self)

    @property
    def users(self):
        return UsersApi(self)

    @property
    def configs(self):
        return ConfigsApi(self)

    @property
    def case_types(self):
        return CaseTypesApi(self)

    @property
    def suites(self):
        return SuitesApi(self)

    @property
    def templates(self):
        return TemplatesApi(self)

    @property
    def case_fields(self):
        return CaseFieldsApi(self)

    @property
    def results_fields(self):
        return ResultsFieldsApi(self)

    @property
    def priorities(self):
        return PrioritiesApi(self)

    @property
    def sections(self):
        return SectionsApi(self)

    @property
    def milestones(self):
        return MilestonesApi(self)

    @property
    def plans(self):
        return PlansApi(self)

    @property
    def results(self):
        return ResultsApi(self)

    @property
    def runs(self):
        return RunsApi(self)

    @property
    def service(self):
        return ServiceApi(self)

    @property
    def shared_steps(self):
        return SharedStepsApi(self)

    @property
    def reports(self):
        return ReportsApi(self)
