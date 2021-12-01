from mlflow.pyfunc import PyFuncModel, load_model
from mlflow import get_tracking_uri
from mlflow.tracking.fluent import Run
from pandas import DataFrame


class MLFlowRun:
    def __init__(self, run: Run, model=None):
        self.run = run
        self._model = model

    @property
    def run_id(self):
        return self.run.info.run_id

    @property
    def run_url(self):
        return f"{get_tracking_uri()}/#/experiments/{self.run.info.experiment_id}/runs/{self.run_id}"

    @property
    def run_url_local(self):
        return f"http://localhost:5000/#/experiments/{self.run.info.experiment_id}/runs/{self.run_id}"

    @property
    def model_flavors(self):
        return self.model.metadata.flavors.keys()

    @property
    def model_uri(self) -> str:
        return f"runs:/{self.run_id}/model"

    @property
    def input_schema(self) -> DataFrame:
        return DataFrame(self.model.metadata.get_input_schema().to_dict())

    @property
    def output_schema(self) -> DataFrame:
        return DataFrame(self.model.metadata.get_output_schema().to_dict())

    @property
    def model(self) -> PyFuncModel:
        # If a model was supplied to the constructor, use that.
        if self._model:
            return self._model
        # Otherwise, load the model from mlflow using its run id.
        else:
            return load_model(self.model_uri)
