import gitlab


def getattr_interceptor(cls):

    def wrapper(obj, item):
        delegate_to = obj.__class__.__name__.lower()
        try:
            return getattr(getattr(obj, delegate_to), item)
        except AttributeError:
            raise AttributeError(f"type object '{obj.__class__.__name__}' has no attribute '{item}'")

    cls.__getattr__ = wrapper
    return cls


def getattribute_interceptor(cls):
    def wrapper(obj, item):
        def get_item(id=None, **kwargs):
            _item = item.split('_')[1]
            _is_list = False
            if _item.endswith('s'):
                _item = _item[:-1]
                _is_list = True
            _cls = globals()[_item.capitalize()]
            target = getattr(obj, f'{_item}s')
            if _is_list or id is None:
                return [_cls(j) for j in target.list(**kwargs)]
            return _cls(target.get(id))

        if item.startswith('get_'):
            return get_item
        else:
            return object.__getattribute__(obj, item)

    cls.__getattribute__ = wrapper
    return cls


@getattribute_interceptor
@getattr_interceptor
class GitLabBase:
    def __eq__(self, other):
        return self.id == other.id


class Job(GitLabBase):
    def __init__(self, job):
        self.job = job


class Pipeline(GitLabBase):
    def __init__(self, pipeline):
        self.pipeline = pipeline


class Project(GitLabBase):
    def __init__(self, project):
        self.project = project


class GitLab(GitLabBase):
    def __init__(self, *args, **kwargs):
        self.gitlab = gitlab.Gitlab(*args, **kwargs)
        self.gitlab.auth()
