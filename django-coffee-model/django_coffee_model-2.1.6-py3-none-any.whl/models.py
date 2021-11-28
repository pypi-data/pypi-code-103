from datetime import datetime

from django.db import models
from django.utils.translation import gettext as _


class CoffeeModelManager(models.Manager):
    use_for_ralated_fields = True

    def get_queryset(self):
        return super().get_queryset()


class DarkCoffeeModelManager(CoffeeModelManager):
    use_for_ralated_fields = True

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__is_null=True)


class CoffeeModel(models.Model):
    objects = CoffeeModelManager()

    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        verbose_name=_("created at"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name=_("updated at"),
        auto_now=True,
    )


class DarkCoffeeModel(CoffeeModel):
    object = DarkCoffeeModelManager()

    class Meta:
        abstrct = True

    deleted_at = models.DateTimeField(
        verbose_name=_("deleted at"),
        blank=True,
        null=True,
        default=None,
    )

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = datetime.now()
        self.save(update_fields=["deleted_at"])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])
