"""
    This module contains all the url rules for the app.
"""

# pragma pylint: disable=invalid-name
import os
from flask import Blueprint

from gaelib.env import get_dashboard_url_prefix
from gaelib.view.base_view import LazyView


auth_urls = Blueprint('auth', __name__)
auth_urls.add_url_rule(
    '/login/',
    view_func=LazyView('gaelib.auth.views.Login', 'login'),
    methods=['POST'])

verification_urls = Blueprint('verification', __name__)
verification_urls.add_url_rule(
    '/verification/',
    view_func=LazyView('gaelib.auth.views.Verification', 'verification'),
    methods=['GET', 'POST'])

dashboard_lib_template_dir = os.path.abspath(
    './lib/dashboard/templates')
dashboard_lib_urls = Blueprint('dashboard_lib', __name__,
                               template_folder=dashboard_lib_template_dir)

dashboard_prefix = get_dashboard_url_prefix()
dashboard_lib_urls.add_url_rule(
    '/' + dashboard_prefix + '/login',
    view_func=LazyView(
        'gaelib.dashboard.views.DashboardLogin',
        'dashboard_login'),
    methods=['GET']
)
dashboard_lib_urls.add_url_rule(
    '/' + dashboard_prefix + '/logout',
    view_func=LazyView(
        'gaelib.dashboard.views.DashboardLogout',
        'dashboard_logout'),
    methods=['GET']
)
dashboard_lib_urls.add_url_rule(
    '/' + dashboard_prefix + '/notifications',
    view_func=LazyView(
        'gaelib.dashboard.views.Notifications',
        'notifications'),
    methods=['GET', 'POST']
)
# dashboard_lib_urls.add_url_rule(
#   '/' + dashboard_prefix + '/logout',
#   view_func=LazyView(
#     'gaelib.auth.views.DashboardLogout',
#     'dashboard_logout'),
#     methods=['GET']
# )


client_logger_urls = Blueprint('clientlogger', __name__)
client_logger_urls.add_url_rule(
    '/clientlogger',
    view_func=LazyView(
        'gaelib.clientlogger.logging.LogApi',
        'logger'),
    methods=['POST']
)
