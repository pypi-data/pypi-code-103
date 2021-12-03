from typing import Type
from django.urls import path
from django.urls.conf import include, path

from wcd_geo_db.client import GeoClient
from wcd_geo_db.contrib.dal.preparators import DivisionsPreparator
from .views import DivisionDalView, DivisionDalViewAdmin


app_name = 'wcd_geo_db_dal'


def i(namespace, *urls):
    return include((urls, app_name), namespace)


def make_divisions_path(
    name: str,
    client: GeoClient,
    cls: Type[DivisionDalView] = DivisionDalView,
    **kwargs
):
    return path(f'{name}/', cls.as_view(
        client=client.bank.divisions,
        preparator=DivisionsPreparator(
            client=client.bank.divisions,
            formatter_client=client.addresses.formatter
        ),
        **kwargs
    ), name=name)


def autocomplete_namespace(*paths):
    return path('', i('wcd-geo-db',
        path('', i('dal',
            path('admin/wcd_geo_db/dal/', i('admin',
                path('autocomplete/', i(
                    'autocomplete',
                    *paths
                )),
            )),
        )),
    ))


def make_urlpatterns(client: GeoClient, *paths):
    return [
        autocomplete_namespace(
            make_divisions_path('divisions', client, cls=DivisionDalViewAdmin),
            *paths
        ),
    ]
