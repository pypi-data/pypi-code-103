import os
import re
from dataclasses import field, dataclass

from cloudrail.knowledge.context.aws.cloudformation.cloudformation_utils import CloudformationUtils
from cloudrail.knowledge.context.iac_type import IacType
from cloudrail.knowledge.utils import file_utils

from cloudrail.cli.commands_utils import exit_with_code, echo_error
from cloudrail.cli.exit_codes import ExitCode
from cloudrail.cli.service.command_parameters import CommandParameters


@dataclass
class BaseCloudformationCommandParameters(CommandParameters):
    api_key: str = None
    iac_type = IacType.CLOUDFORMATION
    cfn_template_file: str = None
    cfn_params: str = None
    cfn_params_file: str = None
    parsed_cfn_params: dict = field(default=dict)
    output_file: str = None

    def validate_and_init_parameters(self):
        if self.cfn_template_file:
            if not os.path.exists(self.cfn_template_file):
                echo_error(f'The CloudFormation template file path you have provided "{self.cfn_template_file}" '
                           f'does not point to a specific file.'
                           '\nPlease provide the path directly to the template file you wish to use Cloudrail with.')
                exit_with_code(ExitCode.INVALID_INPUT)

        self.parsed_cfn_params = self.to_cfn_params_dict()
        if self.cfn_params and not self.parsed_cfn_params:
            echo_error('Invalid CloudFormation parameters format set in "cfn-params" parameter'
                       '\nPlease enter valid format, i.e. myKey1=myValue1,myKey2=myValue2...')
            exit_with_code(ExitCode.INVALID_INPUT)

        if self.cfn_params_file:
            if not os.path.exists(self.cfn_params_file):
                echo_error(f'The CloudFormation parameters file path you have provided "{self.cfn_params_file}" '
                           'does not point to a specific file.'
                           '\nPlease provide the path directly to the parameters file you wish to use Cloudrail with.')
                exit_with_code(ExitCode.INVALID_INPUT)
            else:
                try:
                    parsed_file_cfn_params: dict = self._parse_template_params()
                    if parsed_file_cfn_params:
                        self.parsed_cfn_params.update(parsed_file_cfn_params)
                    else:
                        echo_error('Invalid CloudFormation parameters JSON structure')
                        exit_with_code(ExitCode.INVALID_INPUT)
                except Exception:
                    echo_error(f'Failed to read CloudFormation parameters file="{self.cfn_params_file}"')
                    exit_with_code(ExitCode.INVALID_INPUT)
        self.validate_required_cfn_template_parameters()

    def validate_required_cfn_template_parameters(self):
        if self.cfn_template_file:
            try:
                CloudformationUtils.validate_required_cfn_template_parameters(self.cfn_template_file, self.parsed_cfn_params)
            except Exception as ex:
                echo_error(str(ex))
                exit_with_code(ExitCode.INVALID_INPUT)

    def is_cfn_params_format_valid(self) -> bool:
        if not self.cfn_params:
            return False
        for key_val in re.split(',', self.cfn_params):
            if len(re.split('=', key_val)) != 2:
                return False
        return True

    @staticmethod
    def file_exist(file_path: str):
        try:
            file_utils.validate_file_exist(file_path)
        except Exception as ex:
            echo_error(str(ex))
            exit_with_code(ExitCode.INVALID_INPUT)

    def _parse_template_params(self) -> dict:
        parsed_cfn_params: dict = {}
        cfn_file_params: dict = file_utils.file_to_json(self.cfn_params_file)
        if 'Parameters' in cfn_file_params:
            parsed_cfn_params = cfn_file_params['Parameters']
        elif isinstance(cfn_file_params, list) and cfn_file_params and \
                all({'ParameterKey', 'ParameterValue'}.issubset(set(elm.keys()))
                    for elm in cfn_file_params):
            for key_val in cfn_file_params:
                parsed_cfn_params[key_val['ParameterKey']] = key_val['ParameterValue']
        return parsed_cfn_params

    def to_cfn_params_dict(self) -> dict:
        key_val_params: dict = {}
        if self.is_cfn_params_format_valid():
            return self.convert_key_val_params_to_dict(self.cfn_params)
        return key_val_params

    @staticmethod
    def convert_key_val_params_to_dict(key_val_params: str, delimiter=',') -> dict:
        key_val_params = key_val_params.replace(' ', '')
        params_dict: dict = {}
        for key_val in key_val_params.split(delimiter):
            key_val = key_val.split('=')
            if len(key_val) == 2:
                params_dict[key_val[0]] = key_val[1]
        return params_dict
