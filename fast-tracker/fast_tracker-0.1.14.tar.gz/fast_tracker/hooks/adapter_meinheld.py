# -*- coding: utf-8 -*-

import fast_tracker.api.wsgi_application
import fast_tracker.api.in_function


def instrument_meinheld_server(module):
    def wrap_wsgi_application_entry_point(application, *args, **kwargs):
        application = fast_tracker.api.wsgi_application.WSGIApplicationWrapper(
            application)
        args = [application] + list(args)
        return args, kwargs

    fast_tracker.api.in_function.wrap_in_function(module,
                                                  'run', wrap_wsgi_application_entry_point)
