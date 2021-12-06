from windchill_metric_config.description import Description


def as_yaml_dict(clazz):
    metrics = {}
    for item in clazz.__dict__.keys():
        child = clazz.__getattribute__(item)
        if type(child) == Description:
            metrics[child.id] = child.enabled
        else:
            metrics[item] = child.as_yaml_dict()
    return metrics


def generate_yaml(clazz, yaml_object, comment_indent):
    for item in clazz.__dict__.keys():
        child = clazz.__getattribute__(item)
        if type(child) == Description:
            desc = child.description
            if desc is not 'test' and len(desc) > 0:
                yaml_object.yaml_add_eol_comment(desc, child.id,
                                                 comment_indent)
        else:
            child.generate_yaml(yaml_object[item], comment_indent)
