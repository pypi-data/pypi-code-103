from app.dao.new_email_interactive_dao import NewEmailCli
from app.utils.logger.logging_utils import get_logger
from functools import cached_property


class Router:
    def __init__(self, app, args, logger=None):
        self._logger = logger or get_logger()
        self._app = app
        self._args = args

    @cached_property
    def _switcher(self):
        return {"new-email-interactive": self.new_email_interactive}

    def new_email_interactive(self):
        cli = NewEmailCli(logger=self._logger)
        self._logger.info("Starting new interactive CLI session")
        cli.main()

    def run_workflow(self):
        workflow = self._switcher.get(self._app)
        return workflow()
