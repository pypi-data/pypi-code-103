"""Return types for sensitivity (tests)."""

from typing import Optional

from instancelib.labels import LabelProvider, MemoryLabelProvider
from text_explainability.generation.return_types import Instances

from text_sensitivity.ui.notebook import Render


class SuccessTest(Instances):
    def __init__(self,
                 success_percentage: float,
                 successes,
                 failures,
                 predictions = None,
                 type: str = 'robustness',
                 subtype: str = 'input_space',
                 callargs: Optional[dict] = None,
                 **kwargs):
        super().__init__(instances={'successes': successes, 'failures': failures},
                         type=type,
                         subtype=subtype,
                         callargs=callargs,
                         renderer=Render,
                         **kwargs)
        self.success_percentage = success_percentage
        self.predictions = self.__load_predictions(predictions)

    def __load_predictions(self, predictions):
        if predictions is None:
            return None
        if not isinstance(predictions, LabelProvider):
            return MemoryLabelProvider.from_tuples(predictions)
        return predictions

    @property
    def content(self):
        res = {'success_percentage': self.success_percentage,
               'failure_percentage': 1.0 - self.success_percentage,
               'successes': self.instances['successes'],
               'failures': self.instances['failures']}
        if self.predictions is not None:
            res['predictions'] = self.predictions
        return res
