# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Request type registry for looking up registered request types per name."""


class RequestTypeRegistry:
    """Registry for looking up registerd request types per name."""

    def __init__(self, registered_types):
        """Constructor."""
        self.registered_types = {}
        for request_type in registered_types:
            self.register_type(request_type)

    def register_type(self, request_type, force=False):
        """Register the specified request_type.

        :param request_type: The request type to register.
        :param as_type: Optional, the name under which to register the type.
                        If not specified, the request_type name from the
                        request_class will be taken.
        :param force: Override already registered type, if there is a
                      different type already registered with the same name.
        """
        type_id = request_type.type_id
        if force:
            self.registered_types[type_id] = request_type
        else:
            self.registered_types.setdefault(type_id, request_type)

    def lookup(self, type_id, quiet=False, default=None):
        """Look up a registered type by its name.

        :param type_id: The type name to look up.
        :param quiet: TODO
        :param default: The default value to return if no type is found and
                        quiet is set.
        :return: The type registered for the name.
        """
        if not quiet:
            return self.registered_types[type_id]

        return self.registered_types.get(type_id, default)
