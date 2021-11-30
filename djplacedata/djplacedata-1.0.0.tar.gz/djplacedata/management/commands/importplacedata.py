from django.apps import apps
from django.core.management.base import BaseCommand

from djplacedata.models import Place
from djplacedata.utils import get_place_field_from_model, get_values_from_model


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('app_label')
        parser.add_argument('model_name',)

    def handle(self, *args, **options):
        app_label = options['app_label']
        model_name = options['model_name']

        self.model = apps.get_model(app_label, model_name)
        self.field = get_place_field_from_model(self.model)
        self.values = get_values_from_model(self.model)

        for place, values in self.values.results:
            try:
                self.model.objects.update_or_create(
                    **{self.field: place,},
                    defaults=values)
            except Place.DoesNotExist:
                pass
