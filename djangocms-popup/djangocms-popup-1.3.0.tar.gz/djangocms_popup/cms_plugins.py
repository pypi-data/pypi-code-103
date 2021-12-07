from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext as _

from djangocms_popup.models import PopupPluginModel


@plugin_pool.register_plugin
class PopupPluginPublisher(CMSPluginBase):
    module = _("Popup")
    name = _("Popup Container")
    model = PopupPluginModel
    render_template = "popup/base.html"
    allow_children = True

    def render(self, context, instance, placeholder):
        context.update({"instance": instance})
        return context
