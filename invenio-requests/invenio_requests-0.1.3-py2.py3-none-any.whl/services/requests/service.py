# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Requests service."""

from invenio_db import db
from invenio_records_resources.services import RecordService, ServiceSchemaWrapper
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    RecordDeleteOp,
    unit_of_work,
)

from ...customizations.base import RequestActions
from ...errors import CannotExecuteActionError
from ...proxies import current_events_service, current_registry
from ...records.api import RequestEventType
from ...resolvers import ResolverRegistry
from .links import RequestLinksTemplate


class RequestsService(RecordService):
    """Requests service."""

    @property
    def links_item_tpl(self):
        """Item links template."""
        return RequestLinksTemplate(self.config.links_item, self.config.action_link)

    @property
    def request_type_registry(self):
        """Request_type_registry."""
        return current_registry

    def _wrap_schema(self, schema):
        """Wrap schema."""
        return ServiceSchemaWrapper(self, schema)

    @unit_of_work()
    def create(
        self, identity, data, request_type, receiver, creator=None, topic=None, uow=None
    ):
        """Create a record."""
        self.require_permission(identity, "create")

        # we're not using "self.schema" b/c the schema may differ per request type!
        schema = self._wrap_schema(request_type.marshmallow_schema())
        data, errors = schema.load(
            data,
            context={"identity": identity},
            raise_errors=False,
        )

        # most of the data is initialized via the components
        request = self.record_cls.create(
            {},
            type=request_type,
        )

        creator = (
            ResolverRegistry.reference_entity(creator)
            if creator is not None
            else ResolverRegistry.reference_identity(identity)
        )

        # Run components
        self.run_components(
            "create",
            identity,
            data=data,
            record=request,
            errors=errors,
            created_by=creator,
            topic=ResolverRegistry.reference_entity(topic),
            receiver=ResolverRegistry.reference_entity(receiver),
            uow=uow,
        )

        # persist record (DB and index)
        uow.register(RecordCommitOp(request, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            request,
            schema=schema,
            links_tpl=self.links_item_tpl,
            errors=errors,
        )

    def read(self, id_, identity):
        """Retrieve a request."""
        # resolve and require permission
        request = self.record_cls.get_record(id_)
        self.require_permission(identity, "read", record=request)

        # run components
        for component in self.components:
            if hasattr(component, "read"):
                component.read(identity, record=request)

        return self.result_item(
            self,
            identity,
            request,
            schema=self._wrap_schema(request.type.marshmallow_schema()),
            links_tpl=self.links_item_tpl,
        )

    @unit_of_work()
    def update(self, id_, identity, data, revision_id=None, uow=None):
        """Update a request."""
        request = self.record_cls.get_record(id_)

        # TODO do we need revisions for requests?
        # self.check_revision_id(request, revision_id)

        # check permissions
        self.require_permission(identity, "update", record=request)

        # we're not using "self.schema" b/c the schema may differ per request type!
        schema = self._wrap_schema(request.type.marshmallow_schema())
        data, _ = schema.load(
            data,
            context={
                "identity": identity,
                "record": request,
            },
        )

        # run components
        self.run_components("update", data=data, record=request, uow=uow)

        uow.register(RecordCommitOp(request, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            request,
            schema=schema,
            links_tpl=self.links_item_tpl,
        )

    @unit_of_work()
    def delete(self, id_, identity, uow=None):
        """Delete a request from database and search indexes."""
        request = self.record_cls.get_record(id_)

        # TODO do we need revisions for requests?
        # self.check_revision_id(request, revision_id)

        # check permissions
        self.require_permission(identity, "delete", record=request)

        # TODO:
        # prevent deletion if in open state?

        # run components
        # TODO: fix invenio-records-resources ServiceComponent
        # self.run_components('delete', uow, identity, record=request)

        uow.register(RecordDeleteOp(request, indexer=self.indexer))
        return True

    def reindex(self, identity, params=None, es_preference=None, **kwargs):
        """Reindex records matching the query parameters."""
        # TODO check later
        return super().reindex(identity, params=None, es_preference=None, **kwargs)

    def rebuild_index(self, identity):
        """Reindex all records managed by this service."""
        for req_meta in self.record_cls.model_cls.query.all():
            request = self._request_from_model(req_meta)

            if not request.is_deleted:
                self.indexer.index(request)

    @unit_of_work()
    def execute_action(self, identity, id_, action, data=None, uow=None):
        """Execute the given action for the request, if possible.

        For instance, it would be not possible to execute the specified
        action on the request, if the latter has the wrong status.
        """
        # Retrieve request and action
        request = self.record_cls.get_record(id_)
        action_obj = RequestActions.get_action(request, action)

        # TODO permission checks

        # Check if the action *can* be executed (i.e. correct status etc.)
        if not action_obj.can_execute(identity):
            raise CannotExecuteActionError(action)

        # Execute action and register request for persistence.
        action_obj.execute(identity, uow)
        uow.register(RecordCommitOp(request, indexer=self.indexer))

        # Create action event if defined
        event_type = action_obj.event_type
        if event_type is not None:
            current_events_service.create(
                identity, request.id, {"type": event_type}, uow=uow
            )

        # Assuming that data is just for comment payload
        if data:
            comment_type = RequestEventType.COMMENT.value
            current_events_service.create(
                identity, request.id, {**data, "type": comment_type}, uow=uow
            )

        return self.result_item(
            self,
            identity,
            request,
            schema=self._wrap_schema(request.type.marshmallow_schema()),
            links_tpl=self.links_item_tpl,
        )
