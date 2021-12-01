from breath_data.data_workflow import Workflow
from module.src.breath_data.data_workflow.service import DataWorkflow

class ClimateDataWorkflow(Workflow):

	def __init__(self, workflow_service: DataWorkflow):
		super().__init__(workflow_service, "ClimateDataWorkflow")

	def _workflow_run(self):
		self._download_data()

	def _download_data(self):
		pass