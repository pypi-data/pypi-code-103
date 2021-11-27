import param


class Group(param.Parameterized):
    name = param.String()
    _id = param.String()
    projects = param.List()


class Project(param.Parameterized):
    name = param.String()
    _id = param.String()
    groups = param.List()
