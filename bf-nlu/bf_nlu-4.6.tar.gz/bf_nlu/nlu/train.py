import logging
import typing
from typing import Any, Optional, Text, Tuple, Union, Dict

from bf_nlu.nlu import config
from bf_nlu.nlu.components import ComponentBuilder
from bf_nlu.nlu.config import bf_nluNLUModelConfig
from bf_nlu.nlu.model import Interpreter, Trainer
from bf_nlu.nlu.training_data import load_data
from bf_nlu.nlu.training_data.loading import load_data_from_endpoint
from bf_nlu.utils.endpoints import EndpointConfig


if typing.TYPE_CHECKING:
    from bf_nlu.importers.importer import TrainingDataImporter

logger = logging.getLogger(__name__)


class TrainingException(Exception):
    """Exception wrapping lower level exceptions that may happen while training

      Attributes:
          failed_target_project -- name of the failed project
          message -- explanation of why the request is invalid
      """

    def __init__(
        self,
        failed_target_project: Optional[Text] = None,
        exception: Optional[Exception] = None,
    ) -> None:
        self.failed_target_project = failed_target_project
        if exception:
            self.message = exception.args[0]
        else:
            self.message = ""

    def __str__(self) -> Text:
        return self.message


def create_persistor(persistor: Optional[Text]):
    """Create a remote persistor to store the model if configured."""

    if persistor is not None:
        from bf_nlu.nlu.persistor import get_persistor

        return get_persistor(persistor)
    else:
        return None


async def train(
    nlu_config: Union[Text, Dict, bf_nluNLUModelConfig],
    data: Union[Text, "TrainingDataImporter"],
    path: Optional[Text] = None,
    fixed_model_name: Optional[Text] = None,
    storage: Optional[Text] = None,
    component_builder: Optional[ComponentBuilder] = None,
    training_data_endpoint: Optional[EndpointConfig] = None,
    persist_nlu_training_data: bool = False,
    **kwargs: Any,
) -> Tuple[Trainer, Interpreter, Optional[Text]]:
    """Loads the trainer and the data and runs the training of the model."""
    from bf_nlu.importers.importer import TrainingDataImporter

    if not isinstance(nlu_config, bf_nluNLUModelConfig):
        nlu_config = config.load(nlu_config)

    # Ensure we are training a model that we can save in the end
    # WARN: there is still a race condition if a model with the same name is
    # trained in another subprocess
    trainer = Trainer(nlu_config, component_builder)
    persistor = create_persistor(storage)
    if training_data_endpoint is not None:
        training_data = await load_data_from_endpoint(
            training_data_endpoint, nlu_config.language
        )
    elif isinstance(data, TrainingDataImporter):
        training_data = await data.get_nlu_data(nlu_config.data)
    else:
        training_data = load_data(data, nlu_config.language)

    training_data.print_stats()
    interpreter = trainer.train(training_data, **kwargs)

    if path:
        persisted_path = trainer.persist(
            path, persistor, fixed_model_name, persist_nlu_training_data
        )
    else:
        persisted_path = None

    return trainer, interpreter, persisted_path


if __name__ == "__main__":
    raise RuntimeError(
        "Calling `bf_nlu.nlu.train` directly is no longer supported. Please use "
        "`bf_nlu train` to train a combined Core and NLU model or `bf_nlu train nlu` "
        "to train an NLU model."
    )
