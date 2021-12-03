from typing import Any, List, Optional, Type
from django.db import models, transaction


__all__ = 'MergeCommiter', 'synonyms_splitter', 'inject_synonyms',


class MergeCommiter:
    model: Type[models.Model]
    update_fields: List[str]

    creations: List[models.Model]
    updates: List[models.Model]
    failures: List[Any]

    def __init__(
        self,
        model: Type[models.Model],
        update_fields: List[str],
    ):
        self.model = model
        self.update_fields = update_fields
        self.clear()

    def run(self):
        self.commit()
        self.clear()

    def create(self, item: Any):
        self.creations.append(item)

    def update(self, item: Any):
        self.updates.append(item)

    def fail(self, item: Any, **kwargs):
        self.failures.append((item, kwargs))

    def commit(self):
        # TODO: Work on failures save.
        print(self.failures)

        with transaction.atomic():
            created = self.model.objects.bulk_create(self.creations)
            self.model.objects.bulk_update(
                self.updates, fields=self.update_fields
            )

        return created + self.updates

    def clear(self):
        self.creations = []
        self.updates = []
        self.failures = []

    def __enter__(self):
        return self

    def __exit__(self):
        self.run()


def synonyms_splitter(value: str):
    return {x for x in (s.strip() for s in value.split(',')) if x}


def inject_synonyms(instance: models.Model, name: str, synonyms: Optional[str] = ''):
    items = synonyms_splitter(synonyms)

    if instance.name != name:
        items.add(name)

    if len(items) > 0:
        items |= synonyms_splitter(instance.synonyms)
        instance.synonyms = ','.join(items)

    return instance
