import json
import logging
import os

from karby.parameter_manager import ParameterManager
from karby.sca_apis.SCAScanTool import SCAScanTool
from karby.util.helpers import exec_command, resolve_package_id, write_issue_report, write_component_report, \
     check_mvn_version
from karby.util.models.ComponentReport import ComponentReport
from karby.util.models.IssueReport import IssueReport

FORMAT = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger("scantist-api")

class OWASP(SCAScanTool):
    def __init__(self, param_manager: ParameterManager):
        super().__init__(param_manager)
        self.report_json = os.path.join(self.project_url, 'target', 'dependency-check-report.json')
        self.origin_pom = os.path.join(self.project_url, 'pom.xml')
        self.owasp_script = os.getenv("OWASP_SH", "")

    def check_auth(self):
        """
        OWASP don't need authentication
        :return:
        """
        pass

    def scan_with_api(self):
        if not self.owasp_script:
            raise AttributeError("please specify owasp script path to OWASP_SH in environment")
        cmd = f"{self.owasp_script} -s {self.project_url} -out {self.project_url} -f JSON --disableAssembly"
        logger.info(f"subprocess: {cmd}")
        result = exec_command(cmd)
        if result.get("code") != 0:
            if 'output' in result:
                logger.info(result['output'].decode())
            if 'error' in result:
                logger.info(result['error'].decode())
            raise RuntimeError("owasp mvn dependency check failed.")
        return

    def scan_with_cmd(self):
        check_mvn_version()
        # old solution is to modify pom file, new solution is to trigger the plugin directly
        # backup origin xml
        # shutil.copyfile(self.origin_pom, self.origin_pom_bk)
        # pom_xml = ModifyXML(self.origin_pom_bk)
        # pom_xml.addOWASPPlugin()
        # pom_xml.writeXML(self.origin_pom)
        # if not os.path.isfile(self.origin_pom):
        #     raise AttributeError('pom.xml not found. Require a pom.xml in the project working dir.')
        # cmd = f"cd {self.project_url} && mvn clean verify -Dmaven.test.skip"
        cmd = f'cd {self.project_url} &&' \
              f' mvn org.owasp:dependency-check-maven:6.4.1:aggregate' \
              f' -DassemblyAnalyzerEnabled=false' \
              f' -DnugetconfAnalyzerEnabled=false' \
              f' -DnuspecAnalyzerEnabled=false' \
              f' -DskipProvidedScope=true' \
              f' -DskipTestScope=true' \
              f' -Dformat=JSON'
        logger.info(f"subprocess: {cmd}")
        result = exec_command(cmd)
        if result.get("code") != 0:
            if 'output' in result:
                logger.info(result['output'].decode())
            if 'error' in result:
                logger.info(result['error'].decode())
            raise RuntimeError("owasp mvn dependency check failed.")
        return

    def get_report_by_api(self, scan_feedback=None):
        """
        logic is exactly the same as get report from cmd
        :param scan_feedback:
        :return:
        """
        self.parse_dependency_json()

    def get_report_from_cmd(self, scan_feedback=None):
        self.parse_dependency_json()

    def parse_dependency_json(self):
        if not os.path.isfile(self.report_json):
            self.report_json = os.path.join(self.project_url, 'dependency-check-report.json')
        if not os.path.isfile(self.report_json):
            raise RuntimeError(f"dependency-check-report.json not found in {self.report_json}")
        file = open(self.report_json, 'r')
        dc_report = json.loads(file.read())
        component_list = {}
        issue_list = []
        for dependency in dc_report['dependencies']:
            if "packages" in dependency:
                package_id = dependency['packages'][0]['id']
                group_id, artifact_id, version = resolve_package_id(package_id)
            else:
                artifact_id = dependency['fileName'].strip()
                group_id = artifact_id
                version = 'N.A.'
            component_report_lib = f'{artifact_id} {group_id}'
            issue_report_lib = f'{group_id} {artifact_id}'
            tmp_component = ComponentReport(component_report_lib, version)
            if 'sha256' in dependency:
                sha256 = dependency['sha256']
            else:
                sha256 = tmp_component.get_hash()
            component_list[sha256] = tmp_component
            if 'vulnerabilities' in dependency:
                vul_list = dependency['vulnerabilities']
                for vul in vul_list:
                    tmp_component.get_vul_list().append(vul['name'])
                    tmp_issue = IssueReport(issue_report_lib, version, vul['name'])
                    issue_list.append(tmp_issue)
            if 'relatedDependencies' in dependency:
                for relatDep in dependency['relatedDependencies']:
                    if "packageIds" in relatDep:
                        package_id = relatDep['packageIds'][0]['id']
                        group_id, artifact_id, version = resolve_package_id(package_id)
                        tmp_component = ComponentReport(f'{artifact_id} {group_id}', version)
                        if 'sha256' in relatDep:
                            sha256 = relatDep['sha256']
                        else:
                            sha256 = tmp_component.get_hash()
                        component_list[sha256] = tmp_component
        write_issue_report(
            issue_list, f"owasp-issue-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing owasp-issue-{self.project_name} to {self.output_dir}"
        )
        write_component_report(
            list(component_list.values()), f"owasp-component-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing owasp-component-{self.project_name} to {self.output_dir}"
        )
