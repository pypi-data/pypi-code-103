from django.utils.translation import ugettext_lazy as _

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls


class MarketManagerMarketBrowserMenuItem(MenuItemHook):
    """ This class ensures only authorized users will see the menu entry """

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Market Browser"),
            "fas fa-cube fa-fw",
            "marketmanager:marketbrowser",
            navactive=["marketmanager:marketbrowser"],
        )

    def render(self, request):
        if request.user.has_perm("marketmanager.view_marketbrowser"):
            return MenuItemHook.render(self, request)
        return ""


class MarketManagerMarketManagerMenuItem(MenuItemHook):
    """ This class ensures only authorized users will see the menu entry """

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Market Manager"),
            "fas fa-cube fa-fw",
            "marketmanager:marketmanager",
            navactive=["marketmanager:marketmanager"],
        )

    def render(self, request):
        if request.user.has_perm("marketmanager.view_marketmanager"):
            return MenuItemHook.render(self, request)
        return ""

@hooks.register("menu_item_hook")
def register_menu():
    return MarketManagerMarketBrowserMenuItem()


@hooks.register("menu_item_hook")
def register_menu():
    return MarketManagerMarketManagerMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "marketmanager", r"^marketmanager/")
