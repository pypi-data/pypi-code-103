from . import topic
from . import exercise
from . import task
from . import taskstats
from . import person
from . import project
from . import project_taskstats
from . import project_personstats
from . import personstats
from . import group
from . import grouplist
from . import graph
from . import soup
from . import dia

def setup(app):
    app.connect('env-purge-doc', soup.sphinx_purge_doc)

    topic.setup(app)
    exercise.setup(app)
    task.setup(app)
    taskstats.setup(app)
    person.setup(app)
    project.setup(app)
    project_taskstats.setup(app)
    project_personstats.setup(app)
    personstats.setup(app)
    group.setup(app)
    grouplist.setup(app)
    graph.setup(app)
    dia.setup(app)
