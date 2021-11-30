import logging
import logging.handlers
import os
import platform
import sys

import click

from cloudrail.cli import _version
from cloudrail.cli.service.cloudrail_cli_service import CloudrailCliService
from cloudrail.cli.service.service_response_status import ResponseStatus
from common.api.dtos.report_message_dto import ReportMessageDTO


class CliExecutionReporter:
    def __init__(self, service: CloudrailCliService):
        self.service = service

    def report_execution(self, exit_code):
        try:
            args = sys.argv
            report_data = {
                'command': len(args) > 1 and args[1] or '',
                'system': platform.system().lower(),
                'machine': platform.machine().lower(),
                'version': _version.__version__,
                'run_type': 'docker' if bool(os.environ.get('CLOUDRAIL_CLI_VERSION')) else 'pip',
                'exit_code': exit_code or 0
            }
            api_key_index = '--api-key' in sys.argv and (sys.argv.index('--api-key') + 1)
            api_key = None
            if api_key_index:
                api_key = args[api_key_index]
            self.service.api_key = api_key or self.service.api_key
            if not self.service.api_key:
                return
            response = self.service.upload_report(report_data)
            if response.status == ResponseStatus.SUCCESS:
                report_message: ReportMessageDTO = response.message
                if report_message.messages:
                    for message in report_message.messages:
                        click.echo('\n' + message)
        except Exception:
            logging.exception('report_execution failed')
