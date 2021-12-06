"""Return types for sensitivity (tests)."""

from typing import List, Optional, Union

from instancelib.labels import LabelProvider, MemoryLabelProvider
from text_explainability.generation.return_types import Instances

from text_sensitivity.ui.notebook import Render


class SuccessTest(Instances):
    def __init__(self,
                 success_percentage: float,
                 successes,
                 failures,
                 predictions: Optional[Union[LabelProvider, list, dict]] = None,
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


class LabelMetrics(Instances):
    def __init__(self,
                 instances,
                 label_metrics,
                 type: Optional[str] = 'sensitivity',
                 subtype: Optional[str] = 'label_metrics',
                 callargs: Optional[dict] = None,
                 **kwargs):
        super().__init__(instances, type=type, subtype=subtype, callargs=callargs, renderer=Render, **kwargs)
        self.keys = [k for k, _ in enumerate(label_metrics)]
        self.metric_labels = {k: l for k, (l, _, _) in enumerate(label_metrics)}
        self.metric_attributes = {k: a for k, (_, a, _) in enumerate(label_metrics)}
        self.__metrics = {k: m for k, (_, _, m) in enumerate(label_metrics)}
        self.metrics, self.properties = self.extract_metrics(self.__metrics)

    def extract_metrics(self, metrics: dict):
        # Get all unique property names
        properties = []

        for v in metrics.values():
            for p in dir(v):
                if not p.startswith('_') and not callable(getattr(v, p)) and p not in properties:
                    properties.append(p)

        # Extract property values
        def extract_property(m, p):
            res = getattr(m, p, None)
            if isinstance(res, frozenset):
                res = len(res)
            return res

        return {k: {p: extract_property(v, p) for p in properties} for k, v in metrics.items()}, properties

    @property
    def content(self):
        res = {'label_metrics': [{'label': self.metric_labels[k],
                                  'attribute': self.metric_attributes[k],
                                  'metrics': self.metrics[k]} for k in self.keys]}
        res['metrics'] = self.properties
        return res


class MeanScore(Instances):
    def __init__(self,
                 scores: List[float],
                 label: str,
                 instances,
                 type: Optional[str] = 'sensitivity',
                 subtype: Optional[str] = 'mean_score',
                 callargs: Optional[dict] = None,
                 **kwargs):
        super().__init__(instances, type=type, subtype=subtype, callargs=callargs, renderer=Render, **kwargs)
        self.scores = scores
        self.label = label

    @property
    def content(self):
        return {'scores': self.scores,
                'mean_score': sum(self.scores) / len(self.scores),
                'label': self.label,
                'instances': [i.__dict__ for i in self.instances.get_all()]}  # TODO: should genbase do this?
