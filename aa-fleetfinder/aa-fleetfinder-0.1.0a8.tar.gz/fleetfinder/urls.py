"""
url config
"""

from django.conf.urls import url

from fleetfinder import views

app_name: str = "fleetfinder"

urlpatterns = [
    url(r"^$", views.dashboard, name="dashboard"),
    url(r"^create/$", views.create_fleet, name="create_fleet"),
    url(r"^save/$", views.save_fleet, name="save_fleet"),
    url(r"^join/(?P<fleet_id>[0-9]+)/$", views.join_fleet, name="join_fleet"),
    url(r"^details/(?P<fleet_id>[0-9]+)/$", views.fleet_details, name="fleet_details"),
    url(r"^edit/(?P<fleet_id>[0-9]+)/$", views.edit_fleet, name="edit_fleet"),
    # ajax calls
    url(
        r"^call/dashboard/$",
        views.ajax_dashboard,
        name="ajax_dashboard",
    ),
    url(
        r"^call/details/(?P<fleet_id>[0-9]+)/$",
        views.ajax_fleet_details,
        name="ajax_fleet_details",
    ),
]
