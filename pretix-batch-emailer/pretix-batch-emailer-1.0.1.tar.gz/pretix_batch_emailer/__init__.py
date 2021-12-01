from django.utils.translation import gettext_lazy

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")

__version__ = "1.0.1"


class PluginApp(PluginConfig):
    name = "pretix_batch_emailer"
    verbose_name = "Batch Emailer"

    class PretixPluginMeta:
        name = gettext_lazy("Batch Emailer")
        author = "Lukas Bockstaller"
        description = gettext_lazy(
            "Send a Batch Email to all currently displayed orders. "
        )
        visible = True
        version = __version__
        category = "FEATURE"
        compatibility = "pretix>=3.0"

    def ready(self):
        from . import signals  # NOQA


default_app_config = "pretix_batch_emailer.PluginApp"
