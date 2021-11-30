import json
import logging
import os
import shutil
import tempfile
import traceback
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional

from cloudrail.knowledge.utils import file_utils
from cloudrail.knowledge.utils.terraform_show_output_transformer import TerraformShowOutputTransformer
from cloudrail.knowledge.utils.terraform_output_validator import TerraformOutputValidator

from cloudrail.cli.service.checkov_executor import CheckovExecutor
from cloudrail.cli.spinner_wrapper import SpinnerWrapper
from cloudrail.cli.terraform_service.exceptions import TerraformShowException
from cloudrail.cli.terraform_service.terraform_plan_converter import TerraformPlanConverter
from common.api.dtos.checkov_result_dto import CheckovResultDTO
from common.api.dtos.cloud_provider_dto import CloudProviderDTO
from common.api.dtos.supported_services_response_dto import SupportedSectionDTO
from common.ip_encryption_utils import EncryptionMode, encode_ips_in_json
from common.utils.customer_string_utils import CustomerStringUtils


@dataclass
class TerraformContextResult:
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None


class TerraformContextService:

    def __init__(self, terraform_plan_converter: TerraformPlanConverter, checkov_executor: CheckovExecutor = None):
        self.terraform_plan_converter = terraform_plan_converter
        self.checkov_executor = checkov_executor or CheckovExecutor()
        self.working_dir = None

    def convert_plan_to_json(self, terraform_plan_path: str,
                             terraform_env_path: str,
                             raw: bool,
                             spinner: SpinnerWrapper) -> TerraformContextResult:
        try:
            logging.info('step 1 - copy Terraform data to temp folder')
            working_dir = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
            os.makedirs(working_dir)
            self.working_dir = working_dir
            logging.info('step 2 - Terraform plan to json')
            return TerraformContextResult(True, self._get_terraform_plan_json_file(terraform_plan_path,
                                                                                   terraform_env_path,
                                                                                   working_dir,
                                                                                   raw,
                                                                                   spinner))
        except TerraformShowException as ex:
            logging.exception('error converting plan to json')
            self._clean_env()
            return TerraformContextResult(False, error=str(ex))
        except Exception as ex:
            logging.exception('error converting plan to json')
            self._clean_env()
            return TerraformContextResult(False, error=str(ex))

    def process_json_result(self,
                            plan_json_path: str,
                            services_to_include: Dict[str, SupportedSectionDTO],
                            checkov_results: Dict[str, List[CheckovResultDTO]],
                            customer_id: str,
                            handshake_version: str,
                            base_dir: str,
                            cloud_provider: CloudProviderDTO):
        try:
            CustomerStringUtils.set_hashcode_salt(customer_id)
            dic = file_utils.file_to_json(plan_json_path)
            result_dic = TerraformShowOutputTransformer.transform(plan_json_path, base_dir, services_to_include, customer_id)
            result_dic.update({'checkov_results': checkov_results,
                               'cloud_provider': cloud_provider.value,
                               'handshake_version': handshake_version,
                               'managed_resources_summary': self._create_managed_resources_summary(dic['resource_changes']),
                               'variables': dic.get('variables', {})})
            return TerraformContextResult(True, encode_ips_in_json(json.dumps(result_dic, indent=4, default=vars),
                                                                   customer_id, EncryptionMode.ENCRYPT))
        except Exception as ex:
            logging.exception(f'error while filtering Terraform show output, ex={str(ex)}')
            traceback.print_tb(ex.__traceback__, limit=None, file=None)
            return TerraformContextResult(False, error=str(ex))
        finally:
            self._clean_env()

    @staticmethod
    def read_terraform_output_file(path: str) -> TerraformContextResult:
        try:
            with open(path, 'r') as reader:
                data = reader.read()
                TerraformOutputValidator.validate(data)
                return TerraformContextResult(True, data)
        except Exception as ex:
            logging.exception('error while converting json file to result')
            return TerraformContextResult(False, error=str(ex))

    def _get_terraform_plan_json_file(self,
                                      terraform_plan_path: str,
                                      terraform_env_path: str,
                                      working_dir: str,
                                      raw: bool,
                                      spinner) -> str:
        try:
            plan_json_path = self.terraform_plan_converter.convert_to_json(terraform_plan_path,
                                                                           terraform_env_path,
                                                                           working_dir,
                                                                           raw,
                                                                           spinner)
            logging.info('terraform show ran successfully. output saved to {}'.format(plan_json_path))
            return plan_json_path
        except Exception as err:
            logging.warning('failed getting Terraform file', exc_info=1)
            raise err

    def _clean_env(self):
        if self.working_dir:
            shutil.rmtree(self.working_dir)
        self.working_dir = None

    def run_checkov_checks(self, work_dir: str, checkov_rule_ids: List[str], base_dir: str = None):
        try:
            results = self.checkov_executor.execute_checkov(work_dir, checkov_rule_ids, base_dir)
            return TerraformContextResult(True, result=results)
        except Exception:
            logging.exception('error running checkov checks')
            return TerraformContextResult(True, error={})

    @staticmethod
    def _create_managed_resources_summary(resource_changes):
        total, created, updated, deleted = 0, 0, 0, 0
        for resource in resource_changes:
            actions = resource.get('change', {}).get('actions', [])
            if resource['mode'] != 'managed':
                continue
            if 'create' in actions:
                created += 1
            if 'delete' in actions:
                deleted += 1
            if 'update' in actions:
                updated += 1
            total += 1
        return {'total': total, 'created': created, 'deleted': deleted, 'updated': updated}
