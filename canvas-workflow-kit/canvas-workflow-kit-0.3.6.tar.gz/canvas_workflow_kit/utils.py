import importlib
import inspect
import requests

from canvas_workflow_kit.protocol import ClinicalQualityMeasure


def parse_class_from_python_source(source):
    """
    Parse the python file. Return a ClinicalQualityMeasure class if only one is
    found in the file.
    """

    spec = importlib.util.spec_from_loader('helper', loader=None)
    helper = importlib.util.module_from_spec(spec)

    exec(source, helper.__dict__)

    clinical_quality_measures = []

    for cls_name, cls in inspect.getmembers(helper, inspect.isclass):
        if cls.__module__ != 'helper':
            continue
        if issubclass(cls, ClinicalQualityMeasure):
            clinical_quality_measures.append(cls)

    if len(clinical_quality_measures) == 0:
        raise SyntaxError("No clinical quality measures found.")
    elif len(clinical_quality_measures) > 1:
        raise SyntaxError("More than one clinical quality measures found.")

    return clinical_quality_measures[0]


def send_notification(url, payload={}, headers={}):
    return requests.post(url, data=payload, headers=headers)
