from django.conf import settings
from django.utils.translation import ugettext as _


# Whether to add a button in the CMS toolbar to list all existing popups
ADD_TOOLBAR_BUTTON = getattr(settings, "DJANGOCMS_POPUP_TOOLBAR_BUTTON", True)

POPUP_LIST_TEMPLATES = getattr(
    settings, "DJANGOCMS_POPUP_LIST", (("bottom_right.html", _("Bottom right popup")),)
)

# A toolbar menu identifier to add the button into
TOOLBAR_MENU_IDENTIFIER = getattr(
    settings, "DJANGOCMS_POPUP_TOOLBAR_MENU_IDENTIFIER", None
)

# The position of the button in the toolbar or the menu
TOOLBAR_MENU_POSITION = getattr(settings, "DJANGOCMS_POPUP_TOOLBAR_MENU_POSITION", None)
