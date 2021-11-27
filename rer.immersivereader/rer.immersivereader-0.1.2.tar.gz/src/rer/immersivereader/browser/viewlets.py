# -*- coding: utf-8 -*-
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.layout.viewlets.common import ViewletBase

import logging

logger = logging.getLogger(__name__)


class ImmersiveReaderViewlet(ViewletBase):
    """ """

    def render(self):
        context_state = api.content.get_view(
            context=self.context,
            request=self.request,
            name=u"plone_context_state",
        )
        try:
            enabled_types = api.portal.get_registry_record(
                "rer.immersivereader.enabled_types"
            )
        except InvalidParameterError as e:
            logger.exception(e)
            return ""
        if enabled_types and self.context.portal_type not in enabled_types:
            return ""
        if context_state.canonical_object() == api.portal.get():
            return ""
        if not context_state.is_view_template():
            return ""
        if not getattr(self.context, "text", None):
            return ""
        return self.index()
