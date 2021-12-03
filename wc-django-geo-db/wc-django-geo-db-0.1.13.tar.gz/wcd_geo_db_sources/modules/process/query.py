from django.db import models

from .const import ProcessStatus


__all__ = (
    'IN_PROGRESS',
    'RERUNNABLES',

    'ProcessStateQuerySet',
)

IN_PROGRESS = {
    ProcessStatus.NEW,
    ProcessStatus.IN_PROGRESS
}
RERUNNABLES = IN_PROGRESS | {
    ProcessStatus.FAILED,
}


class ProcessStateQuerySet(models.QuerySet):
    def may_run(self):
        return self.filter(status__in=IN_PROGRESS)

    def may_rerun(self):
        return self.filter(status__in=RERUNNABLES)
