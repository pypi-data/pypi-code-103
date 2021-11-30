import json
import logging
import os
import platform
import re
import shutil
from pathlib import Path
from typing import Optional

import click
import python_terraform
from semantic_version import Version

from cloudrail.cli.terraform_service.custom_tf_versions import get_custom_tf_versions
from cloudrail.cli.terraform_service.exceptions import TerraformShowException
from cloudrail.cli.terraform_service.terraform_raw_data_explorer import TerraformRawDataExplorer
from cloudrail.knowledge.utils import file_utils


class TerraformPlanConverter:

    def convert_to_json(self,
                        terraform_plan_path: str,
                        terraform_env_path: str,
                        working_dir: str,
                        raw: bool,
                        spinner=None) -> str:
        try:
            TerraformRawDataExplorer.update_working_dir(terraform_env_path)
            if raw:
                tf_path = self.prepare_terraform('1.0.0', spinner)
                state_path = None
            else:
                plan_folder = self._uncompress_plan(terraform_plan_path, working_dir)
                state_path = self._get_state_file(plan_folder)
                tf_version = self._extract_tf_version(state_path)
                tf_path = self.prepare_terraform(tf_version, spinner)
            target_plugins_path = os.getenv('TF_PLUGINS_PATH', os.path.join(Path.home(), '.cloudrail', 'terraform_plugins'))
            override_data_dir_path = self._create_override_data_dir_path(terraform_env_path, working_dir)
            output_path = os.path.join(working_dir, 'output.json')
            if spinner:
                spinner.start('Re-running your Terraform plan through a customized \'terraform plan\' to generate needed context data...')
            json_output = self._run_terraform_show(tf_path,
                                                   terraform_plan_path,
                                                   terraform_env_path,
                                                   target_plugins_path,
                                                   override_data_dir_path,
                                                   output_path,
                                                   state_path,
                                                   raw)
            return json_output
        finally:
            TerraformRawDataExplorer.reset_working_dir()

    @staticmethod
    def _create_override_data_dir_path(terraform_env_path: str, working_dir: str) -> str:
        override_data_dir_path = os.path.join(working_dir, '.cloudrail')
        os.mkdir(override_data_dir_path)
        original_modules_dir = os.path.join(terraform_env_path, '.terraform/modules')
        if os.path.isdir(original_modules_dir):
            new_module_dir = os.path.join(override_data_dir_path, 'modules')
            os.symlink(original_modules_dir, new_module_dir)
        return override_data_dir_path

    @staticmethod
    def _run_terraform_show(tf_path: str,
                            plan_path: str,
                            terraform_env_path: str,
                            plugins_path: str,
                            override_data_dir_path: str,
                            output_path: str,
                            state_path: str,
                            raw: bool) -> str:
        logging.info(f'running Terraform with {tf_path}, {plan_path}, {terraform_env_path}, {plugins_path}, {override_data_dir_path}, {output_path}')
        terraform = python_terraform.Terraform(working_dir=terraform_env_path, terraform_bin_path=tf_path, state=state_path)
        logging.info('running Terraform show')
        args = {'no_color': python_terraform.IsFlagged,
                'json': True,
                'plugin_cache_dir': plugins_path,
                'override_data_dir': override_data_dir_path}
        if raw:
            args['raw'] = True
        show_output = terraform.show_cmd(plan_path or '', **args)
        if show_output[0] != 0:
            raise TerraformShowException(TerraformPlanConverter._get_error_from_output(show_output[1]))
        result = show_output[1][2:]
        result_obj = json.loads(result)
        if 'resource_changes' not in result_obj:
            logging.error('terraform show output: {}'.format(show_output[1]))
            logging.error('terraform show logs: {}'.format(show_output[2]))
            raise TerraformShowException(TerraformPlanConverter._get_generic_error())
        file_utils.write_to_file(output_path, result)
        return output_path

    @staticmethod
    def _uncompress_plan(plan_path: str, working_dir: str) -> str:
        plan_folder = os.path.join(working_dir, 'plan_folder')
        logging.info('uncompressing Terraform plan {} to {}'.format(plan_path, plan_folder))
        try:
            shutil.unpack_archive(plan_path, plan_folder, 'zip')
        except Exception:
            raise TerraformShowException("""This Terraform plan file has been generated with an unsupported version of Terraform.
Cloudrail supports versions 0.12-1.0""")
        return plan_folder

    @staticmethod
    def _get_state_file(plan_folder: str) -> str:
        state_name = 'tfstate'
        state_path = os.path.join(plan_folder, state_name)
        if os.path.isfile(state_path):
            return state_path
        else:
            raise TerraformShowException('tfstate was not found in working dir')

    @staticmethod
    def _extract_tf_version(state_path: str) -> str:
        data = file_utils.file_to_json(state_path)
        terraform_version = data['terraform_version']
        logging.info('terraform version {}'.format(terraform_version))
        return terraform_version

    @classmethod
    def prepare_terraform(cls, tf_version: str, spinner=None) -> str:
        tf_binary_cache_dir = os.getenv('TF_BINARY_CACHE', os.path.join(Path.home(), '.cloudrail', 'tf_binary_cache'))
        os.makedirs(tf_binary_cache_dir, exist_ok=True)
        parsed_version = Version(tf_version)
        major_minor_version = '{}.{}'.format(parsed_version.major, parsed_version.minor)
        custom_tf_name = cls._get_custom_terraform_name(major_minor_version)
        custom_tf_cache_dir = os.path.join(tf_binary_cache_dir, major_minor_version)
        os.makedirs(custom_tf_cache_dir, exist_ok=True)
        custom_tf_path = os.path.join(custom_tf_cache_dir, custom_tf_name)
        if spinner and not os.path.isfile(custom_tf_path):
            spinner.succeed()
            click.echo('Downloading a custom Terraform Core binary created by Cloudrail, '
                       'this is only needed once in a while and will take a few minutes.'
                       ' No data is being sent at this time...')
        for file_name in os.listdir(custom_tf_cache_dir):
            file_path = os.path.join(custom_tf_cache_dir, file_name)
            if not os.path.isfile(file_path):
                continue
            if custom_tf_name not in file_path:
                os.remove(file_path)
        cls._download_terraform(custom_tf_name, custom_tf_path)
        return custom_tf_path

    @staticmethod
    def _get_error_from_output(errors: str) -> str:
        logging.error('terraform raw show error: {}'.format(errors))
        parsed_error = TerraformPlanConverter._get_future_syntax_errors(errors) or \
                       TerraformPlanConverter._get_file_not_found(errors) or \
                       TerraformPlanConverter._get_raw_errors(errors) or \
                       TerraformPlanConverter._get_generic_error()
        logging.error('terraform parsed_error: {}'.format(parsed_error))
        return parsed_error

    @staticmethod
    def _get_future_syntax_errors(errors: str) -> Optional[str]:
        known_future_syntax = ['Custom variable validation is experimental',
                               'Reserved argument name in module block',
                               'Provider source not supported']
        future_syntax_regex = '({})'.format('|'.join(known_future_syntax))
        future_syntax_msg = """You are using an unsupported capability ({}). This will be supported at a later date.
In the meantime, please run your TF code with versions 0.12-1.0 and remove any unsupported syntax."""
        future_synatx = set(re.findall(future_syntax_regex, errors))
        if future_synatx:
            return future_syntax_msg.format(','.join(future_synatx))
        else:
            return None

    @staticmethod
    def _get_raw_errors(errors: str):
        error_lines = errors.split('\n')
        error_message = []
        in_error = False
        for line in error_lines:
            if not line:
                continue
            if line.startswith('Warning:') or line.startswith('e:'):
                in_error = False
            if in_error or line.startswith('Error:'):
                in_error = True
                error_message.append(line)
        if error_message:
            return '\n'.join(error_message)
        else:
            return None

    @staticmethod
    def _get_file_not_found(errors: str):
        no_file_regex = r'no file exists at (.*)\.'
        no_file_result = re.findall(no_file_regex, errors)
        if no_file_result:
            file_name = no_file_result[0]
            tf_errors = TerraformPlanConverter._get_raw_errors(errors) or ''
            return f'{tf_errors}' \
                   f'\n\nThe file {file_name} is not found. ' \
                   f'This may be caused by the use of the -v flag when executing this container.' \
                   '\nMake sure that all of the Terraform and related files are included within the path that is mounted.'
        else:
            return None

    @staticmethod
    def _get_generic_error():
        return 'terraform show command returned invalid result'

    @staticmethod
    def _download_terraform(custom_tf_name, custom_tf_path):
        dir_name = os.path.dirname(custom_tf_path)
        os.makedirs(dir_name, exist_ok=True)
        custom_tf_bucket_url = 'https://indeni-cloud-rail-custom-terraform.s3.amazonaws.com/{}'.format(custom_tf_name)
        file_utils.download_signed_file(custom_tf_bucket_url, custom_tf_path)

    @staticmethod
    def _get_custom_terraform_version(major_minor_version: str) -> str:
        custom_tf_versions = get_custom_tf_versions()
        custom_tf_version = custom_tf_versions['versions'].get(major_minor_version)
        if not custom_tf_version:
            raise TerraformShowException("""This Terraform plan file has been generated with an unsupported version {} of Terraform.
            Cloudrail supports versions 0.12-1.0""".format(major_minor_version))
        return custom_tf_version

    @staticmethod
    def _get_custom_terraform_architecture(major_minor_version: str) -> str:
        custom_tf_versions = get_custom_tf_versions()
        supported_archs = custom_tf_versions['architectures'].get(major_minor_version)
        system = platform.system().lower()
        machine = platform.machine().lower()
        machine_converter = {'x86_64': 'amd64', 'aarch64': 'arm64'}
        machine = machine_converter.get(machine, machine)
        architecture = f'{system}-{machine}'
        if not architecture in supported_archs:
            raise TerraformShowException(f'You are using an unsupported architecture {platform.uname()}')
        return architecture

    @classmethod
    def _get_custom_terraform_name(cls, major_minor_version: str):
        version = cls._get_custom_terraform_version(major_minor_version)
        arch = cls._get_custom_terraform_architecture(major_minor_version)
        name = f'custom-terraform-{arch}-{major_minor_version}-{version}'
        return name
