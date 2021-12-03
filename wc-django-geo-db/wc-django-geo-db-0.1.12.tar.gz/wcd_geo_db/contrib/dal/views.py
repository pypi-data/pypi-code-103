from typing import Type
from django.db import models
from dal_select2.views import Select2QuerySetView
from django.utils.translation import get_language
from px_client_builder import Client
from wcd_geo_db.modules.bank.client import DivisionsClient
from wcd_geo_db.modules.addresses.client import FormatterClient

from .preparators import DivisionsPreparator, Preparator


__all__ = (
    'GenericDalView',
    'AdminGateMixin',
    'DivisionDalView',
    'DivisionDalViewAdmin',
)


class GenericDalView(Select2QuerySetView):
    client: Client = None
    find_parameters: dict = {}
    use_simple_search: bool = True

    def get_queryset(self):
        return self.get_search_results(self.client._qs, self.q)

    def get_find_parameters(self):
        return self.find_parameters

    def get_search_results(self, qs: models.QuerySet, q: str):
        return self.client.find(**{
            **self.get_find_parameters(),
            'search_query': {'query': q, 'use_simple_search': self.use_simple_search},
        })

    def prepare_result(self, data):
        return data

    def get_results(self, context):
        """Return data for the 'results' key of the response."""
        return [
            {
                'id': self.get_result_value(result),
                'text': self.get_result_label(result),
                'selected_text': self.get_selected_result_label(result),
            }
            for result in self.prepare_result(context['object_list'])
            if result is not None
        ]


class AdminGateMixin:
    def get_search_results(self, qs: models.QuerySet, q: str):
        o = qs.model._meta
        user = self.request.user

        if not (
            user.is_authenticated
            and user.is_staff
            and (
                user.has_perm(f'{o.app_label}.view_{o.model_name}')
                or user.has_perm(f'{o.app_label}.change_{o.model_name}')
            )
        ):
            return qs.none()

        return super().get_search_results(qs, q)


class PreparatorDalView(GenericDalView):
    preparator: Preparator = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        assert self.preparator is not None, (
            'You must either define `preparator` property or provide '
            'one to `init`.'
        )

    def prepare_result(self, data):
        return self.preparator.prepare(data)

    def get_result_label(self, result):
        return self.preparator.get_label(result)

    def get_result_value(self, result):
        return self.preparator.get_value(result)


class DivisionDalView(PreparatorDalView):
    client: DivisionsClient = None
    preparator: DivisionsPreparator = None

    def prepare_result(self, ids):
        return self.preparator.prepare(ids, get_language())


class DivisionDalViewAdmin(AdminGateMixin, DivisionDalView):
    pass
