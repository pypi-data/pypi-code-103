class BaseLabeler(object):

    def __init__(self, graph, project):
        self.graph = graph
        self.project = project

    def label_raw(self, patterns, label, version=None, parameters=None):
        out = []
        for pattern, parameter_set in zip(patterns, parameters):
            full_query = pattern + ' RETURN r.task as task, r.start as start, r.end as end, r.text as text'
            results = self.graph.query(full_query, parameter_set)
            for result in results:
                out.append(result)
                # self.project.create_prediction(task_id=task, result=[{
                #     'from_name': 'label',
                #     'to_name': 'text',
                #     'type': 'choices',
                #     'value': {
                #         'choices': [label]
                #     }
                # }], model_version=version)
        return out

    def label(self, patterns):
        pass

    def push(self):
        pass
