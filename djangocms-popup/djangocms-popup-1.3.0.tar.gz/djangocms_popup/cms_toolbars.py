# Third party
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from cms.utils.urlutils import admin_reverse
from django.utils.translation import ugettext_lazy as _

from djangocms_popup import settings


class DjangocmsPopupToolbar(CMSToolbar):
    def populate(self):
        url = admin_reverse("djangocms_popup_popuppluginmodel_changelist")

        menu = self.toolbar
        if settings.TOOLBAR_MENU_IDENTIFIER is not None:
            custom_menu = self.toolbar.get_menu(settings.TOOLBAR_MENU_IDENTIFIER)
            if custom_menu is not None:
                menu = custom_menu

        menu.add_link_item(
            name=_("Popup list"),
            url=url,
            position=settings.TOOLBAR_MENU_POSITION,
        )


if settings.ADD_TOOLBAR_BUTTON:
    # register the toolbar only if setting does not exist or is set to true
    toolbar_pool.register(DjangocmsPopupToolbar)
